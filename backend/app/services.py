from collections import Counter, defaultdict
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from sklearn.metrics.pairwise import cosine_similarity
from .models import Paper, PaperAuthor, Author, Topic, PaperTopic, JobPosting
from .nlp.pipeline import clean_text, extract_keywords, tfidf_matrix


def paper_dict(p: Paper) -> dict:
    return {"id":p.id,"title":p.title,"abstract":p.abstract,"year":p.year,"venue":p.venue,"doi":p.doi,"citations":p.citations,"url":p.url,"domain":p.domain,
            "authors":[x.author.name for x in p.authors],"topics":[x.topic.name for x in p.topics]}


def save_paper(db: Session, payload: dict, paper: Paper | None = None) -> Paper:
    paper = paper or Paper()
    for key in ("title", "abstract", "year", "venue", "doi", "citations", "url", "domain"):
        setattr(paper, key, payload.get(key, getattr(paper, key, None)))
    db.add(paper); db.flush()
    if "authors" in payload:
        paper.authors.clear()
        for position, name in enumerate(dict.fromkeys(payload["authors"])):
            author = db.query(Author).filter(func.lower(Author.name) == name.lower()).first()
            if not author:
                author = Author(name=name.strip()); db.add(author); db.flush()
            paper.authors.append(PaperAuthor(author=author, position=position))
    if "topics" in payload:
        paper.topics.clear()
        for name in dict.fromkeys(payload["topics"]):
            topic = db.query(Topic).filter(func.lower(Topic.name) == name.lower()).first()
            if not topic:
                topic = Topic(name=name.strip()); db.add(topic); db.flush()
            paper.topics.append(PaperTopic(topic=topic))
    db.commit(); db.refresh(paper)
    return paper


def recommend(db: Session, paper_id: int, limit: int = 5) -> list[dict]:
    papers = db.query(Paper).options(joinedload(Paper.authors).joinedload(PaperAuthor.author), joinedload(Paper.topics).joinedload(PaperTopic.topic)).all()
    selected = next((p for p in papers if p.id == paper_id), None)
    if not selected or len(papers) < 2:
        return []
    texts = [clean_text(p.title + " " + p.abstract + " " + " ".join(x.topic.name for x in p.topics)) for p in papers]
    matrix, _ = tfidf_matrix(texts)
    if matrix is None: return []
    scores = cosine_similarity(matrix[papers.index(selected)], matrix).ravel()
    ranked = sorted(((float(score), p) for score, p in zip(scores, papers) if p.id != paper_id), reverse=True, key=lambda x:x[0])[:limit]
    return [{**paper_dict(p), "similarity": round(score, 4)} for score,p in ranked]


def analytics(db: Session) -> dict:
    papers = db.query(Paper).options(joinedload(Paper.topics).joinedload(PaperTopic.topic)).all()
    yearly, domains, topic_year = Counter(), Counter(), defaultdict(Counter)
    for p in papers:
        if p.year: yearly[p.year] += 1
        domains[p.domain or "Other"] += 1
        for link in p.topics:
            topic_year[link.topic.name][p.year or 0] += 1
    counts = Counter({k: sum(v.values()) for k,v in topic_year.items()})
    return {"total_papers":len(papers),"total_authors":db.query(Author).count(),"total_topics":db.query(Topic).count(),"total_citations":sum(p.citations for p in papers),
      "yearly":[{"year":k,"papers":v} for k,v in sorted(yearly.items())],"domains":[{"domain":k,"papers":v} for k,v in domains.most_common()],
      "topics":[{"topic":k,"papers":v} for k,v in counts.most_common(12)],"topic_yearly":[{"topic":t,"year":y,"papers":n} for t,ys in topic_year.items() for y,n in sorted(ys.items()) if y]}


def topic_trends(db: Session) -> list[dict]:
    rows = db.query(Topic).options(joinedload(Topic.papers).joinedload(PaperTopic.paper)).all()
    result=[]
    for topic in rows:
        yearly=Counter(link.paper.year for link in topic.papers if link.paper.year)
        years=sorted(yearly)
        recent=sum(yearly[y] for y in years[-2:]); previous=sum(yearly[y] for y in years[-4:-2])
        growth=round((recent-previous)*100/max(previous,1),1) if years else 0
        result.append({"id":topic.id,"name":topic.name,"papers":len(topic.papers),"average_citations":round(sum(x.paper.citations for x in topic.papers)/max(1,len(topic.papers)),1),"first_year":years[0] if years else None,"latest_year":years[-1] if years else None,"growth_percent":growth,"yearly":[{"year":y,"papers":n} for y,n in sorted(yearly.items())]})
    return sorted(result,key=lambda t:t["papers"],reverse=True)


def job_analytics(db: Session) -> dict:
    jobs=db.query(JobPosting).all(); skills=Counter(); roles=Counter(); locations=Counter()
    for job in jobs:
        roles[job.title]+=1; locations[job.location]+=1
        skills.update(s.strip().lower() for s in job.skills.split(",") if s.strip())
    return {"sample_data":True,"total_jobs":len(jobs),"skills":[{"skill":k,"count":v} for k,v in skills.most_common(20)],"roles":[{"role":k,"count":v} for k,v in roles.most_common(10)],"locations":[{"location":k,"count":v} for k,v in locations.most_common(10)]}


def answer_question(db: Session, question: str) -> tuple[str,list[dict]]:
    q=question.lower(); papers=db.query(Paper).options(joinedload(Paper.authors).joinedload(PaperAuthor.author),joinedload(Paper.topics).joinedload(PaperTopic.topic)).all()
    if any(x in q for x in ("fastest", "emerging", "growing", "declining", "trend")):
        trends=topic_trends(db); chosen=sorted(trends,key=lambda x:x["growth_percent"],reverse="emerging" in q or "fastest" in q)[:5]
        return ("Based on the stored publication records, topic movement is: " + "; ".join(f"{x['name']} ({x['growth_percent']:+.1f}%, {x['papers']} papers)" for x in chosen), [])
    if "citation" in q or "most cited" in q:
        matches=sorted(papers,key=lambda p:p.citations,reverse=True)[:5]
    else:
        tokens=set(extract_keywords(question,8)); matches=sorted(papers,key=lambda p:len(tokens & set(extract_keywords(p.title+" "+p.abstract,30))),reverse=True)[:5]
    matches=[p for p in matches if p.title]
    if not matches: return ("I couldn't find a matching paper in the local catalogue. Try a topic, author, or keyword present in the imported records.",[])
    refs=[paper_dict(p) for p in matches]
    return ("I found these relevant catalogue records: " + "; ".join(f"{p['title']} ({p['year'] or 'year unavailable'}, {p['citations']} citations)" for p in refs),refs)
