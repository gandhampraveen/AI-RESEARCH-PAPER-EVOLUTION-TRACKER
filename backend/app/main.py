import csv, io, logging
from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from .config import settings
from .database import Base, engine, get_db
from .models import User, Paper, Author, PaperAuthor, Topic, PaperTopic, ChatMessage, JobPosting
from .schemas import RegisterIn, LoginIn, PaperIn, ChatIn
from .security import hash_password, verify_password, create_token, current_user, admin_user
from .services import paper_dict, save_paper, recommend, analytics, topic_trends, job_analytics, answer_question

logging.basicConfig(level=logging.INFO)
log=logging.getLogger("tracker")
Base.metadata.create_all(bind=engine)
app=FastAPI(title=settings.app_name, version="1.0.0", description="Local research literature and job market analytics API. Sample records are explicitly identified.")
app.add_middleware(CORSMiddleware, allow_origins=settings.origin_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
api="/api"

@app.get("/health")
@app.get(api+"/health")
def health(db: Session=Depends(get_db)):
    try: db.execute(__import__('sqlalchemy').text("SELECT 1")); return {"status":"ok","database":"connected"}
    except Exception as exc: raise HTTPException(503,"Database unavailable") from exc

@app.post(api+"/auth/register",status_code=201)
def register(body:RegisterIn,db:Session=Depends(get_db)):
    if db.query(User).filter(User.email==body.email.lower()).first(): raise HTTPException(409,"Email already registered")
    user=User(name=body.name,email=body.email.lower(),password_hash=hash_password(body.password),role="USER"); db.add(user); db.commit(); db.refresh(user)
    return {"access_token":create_token(user),"token_type":"bearer","user":{"id":user.id,"name":user.name,"email":user.email,"role":user.role}}

@app.post(api+"/auth/login")
def login(body:LoginIn,db:Session=Depends(get_db)):
    user=db.query(User).filter(User.email==body.email.lower()).first()
    if not user or not verify_password(body.password,user.password_hash): raise HTTPException(401,"Incorrect email or password")
    return {"access_token":create_token(user),"token_type":"bearer","user":{"id":user.id,"name":user.name,"email":user.email,"role":user.role}}

@app.get(api+"/auth/me")
def me(user:User=Depends(current_user)): return {"id":user.id,"name":user.name,"email":user.email,"role":user.role}
@app.post(api+"/auth/logout")
def logout(user:User=Depends(current_user)): return {"message":"Signed out. Remove the local access token to end this session."}

@app.get(api+"/papers")
def list_papers(q:str="",year:int|None=None,topic:str|None=None,author:str|None=None,domain:str|None=None,sort:str="year",page:int=1,size:int=20,db:Session=Depends(get_db)):
    query=db.query(Paper).options(joinedload(Paper.authors).joinedload(PaperAuthor.author),joinedload(Paper.topics).joinedload(PaperTopic.topic))
    if q: query=query.filter(or_(Paper.title.ilike(f"%{q}%"),Paper.abstract.ilike(f"%{q}%"),Paper.doi.ilike(f"%{q}%")))
    if year: query=query.filter(Paper.year==year)
    if domain: query=query.filter(Paper.domain.ilike(f"%{domain}%"))
    if topic: query=query.join(Paper.topics).join(PaperTopic.topic).filter(Topic.name.ilike(f"%{topic}%"))
    if author: query=query.join(Paper.authors).join(PaperAuthor.author).filter(Author.name.ilike(f"%{author}%"))
    from sqlalchemy import func
    total=query.distinct().count(); order=Paper.citations.desc() if sort=="citations" else func.coalesce(Paper.year,0).desc()
    items=query.distinct().order_by(order).offset((max(page,1)-1)*min(max(size,1),100)).limit(min(max(size,1),100)).all()
    return {"items":[paper_dict(p) for p in items],"total":total,"page":page,"size":size}

@app.post(api+"/papers",status_code=201)
def create_paper(body:PaperIn,db:Session=Depends(get_db),user:User=Depends(current_user)):
    if body.doi and db.query(Paper).filter(Paper.doi==body.doi).first(): raise HTTPException(409,"A paper with this DOI already exists")
    return paper_dict(save_paper(db,body.model_dump()))
@app.get(api+"/papers/{paper_id}")
def get_paper(paper_id:int,db:Session=Depends(get_db)):
    p=db.query(Paper).options(joinedload(Paper.authors).joinedload(PaperAuthor.author),joinedload(Paper.topics).joinedload(PaperTopic.topic)).filter(Paper.id==paper_id).first()
    if not p: raise HTTPException(404,"Paper not found")
    return paper_dict(p)
@app.put(api+"/papers/{paper_id}")
def update_paper(paper_id:int,body:PaperIn,db:Session=Depends(get_db),user:User=Depends(current_user)):
    p=db.get(Paper,paper_id)
    if not p: raise HTTPException(404,"Paper not found")
    return paper_dict(save_paper(db,body.model_dump(),p))
@app.delete(api+"/papers/{paper_id}",status_code=204)
def delete_paper(paper_id:int,db:Session=Depends(get_db),user:User=Depends(current_user)):
    p=db.get(Paper,paper_id)
    if not p: raise HTTPException(404,"Paper not found")
    db.delete(p); db.commit()

@app.get(api+"/authors")
def authors(db:Session=Depends(get_db)):
    rows=db.query(Author).order_by(Author.name).all()
    return [{"id":a.id,"name":a.name,"affiliation":a.affiliation,"paper_count":db.query(PaperAuthor).filter(PaperAuthor.author_id==a.id).count()} for a in rows]
@app.get(api+"/topics")
def topics(db:Session=Depends(get_db)): return topic_trends(db)
@app.get(api+"/topics/emerging")
def emerging(db:Session=Depends(get_db)): return sorted(topic_trends(db),key=lambda x:x["growth_percent"],reverse=True)[:10]
@app.get(api+"/topics/declining")
def declining(db:Session=Depends(get_db)): return sorted(topic_trends(db),key=lambda x:x["growth_percent"])[:10]
@app.get(api+"/topics/{topic_id}")
def topic_detail(topic_id:int,db:Session=Depends(get_db)):
    found=next((t for t in topic_trends(db) if t["id"]==topic_id),None)
    if not found: raise HTTPException(404,"Topic not found")
    return found
@app.get(api+"/trends")
def trends(db:Session=Depends(get_db)): return topic_trends(db)
@app.get(api+"/trends/yearly")
def trends_yearly(db:Session=Depends(get_db)): return analytics(db)["topic_yearly"]
@app.get(api+"/dashboard")
def dashboard(db:Session=Depends(get_db)): return analytics(db)
@app.get(api+"/papers/{paper_id}/recommendations")
def recommendations(paper_id:int,limit:int=5,db:Session=Depends(get_db)): return recommend(db,paper_id,min(max(limit,1),20))
@app.get(api+"/search")
def search(q:str=Query(min_length=1),db:Session=Depends(get_db)):
    papers=db.query(Paper).filter(or_(Paper.title.ilike(f"%{q}%"),Paper.abstract.ilike(f"%{q}%"))).limit(20).all()
    authors=db.query(Author).filter(Author.name.ilike(f"%{q}%")).limit(10).all(); topics_=db.query(Topic).filter(Topic.name.ilike(f"%{q}%")).limit(10).all()
    jobs=db.query(JobPosting).filter(or_(JobPosting.title.ilike(f"%{q}%"),JobPosting.skills.ilike(f"%{q}%"))).limit(10).all()
    return {"papers":[paper_dict(p) for p in papers],"authors":[{"id":a.id,"name":a.name} for a in authors],"topics":[{"id":t.id,"name":t.name} for t in topics_],"jobs":[{"id":j.id,"title":j.title,"company":j.company,"is_sample":j.is_sample} for j in jobs]}
@app.post(api+"/chat")
def chat(body:ChatIn,db:Session=Depends(get_db)):
    answer,refs=answer_question(db,body.question); db.add(ChatMessage(question=body.question,answer=answer)); db.commit()
    return {"answer":answer,"references":refs,"mode":"local-retrieval"}
@app.get(api+"/jobs/analytics")
def jobs(db:Session=Depends(get_db)): return job_analytics(db)
@app.get(api+"/career-insights")
def career(db:Session=Depends(get_db)):
    data=job_analytics(db); skillmap={"Generative AI":["python","machine learning","nlp","deep learning"],"Natural Language Processing":["python","nlp","machine learning"],"Computer Vision":["python","deep learning","pytorch"],"Data Science":["python","sql","data science"]}
    demand={x["skill"]:x["count"] for x in data["skills"]}
    return [{"topic":t["name"],"skills":[{"name":s,"job_count":demand.get(s.lower(),0)} for s in skillmap.get(t["name"],[])],"research_papers":t["papers"]} for t in topic_trends(db)]
@app.get(api+"/predictions")
def predictions(db:Session=Depends(get_db)):
    out=[]
    for topic in topic_trends(db):
        hist=topic["yearly"]
        if len(hist)>=2:
            vals=[x["papers"] for x in hist[-3:]]; avg=sum(vals)/len(vals); slope=(vals[-1]-vals[0])/max(1,len(vals)-1)
            out.append({"topic":topic["name"],"history":hist,"prediction_year":hist[-1]["year"]+1,"predicted_papers":max(0,round(avg+slope)),"method":"linear trend estimate","caveat":"Directional estimate from a small historical series; not a guaranteed forecast."})
    return out
@app.post(api+"/nlp/keywords")
def keywords(text:str=Query(min_length=3)): 
    from .nlp.pipeline import clean_text,extract_keywords
    return {"cleaned_text":clean_text(text),"keywords":extract_keywords(text)}
@app.post(api+"/admin/import/{kind}")
async def import_csv(kind:str,file:UploadFile=File(...),db:Session=Depends(get_db),admin:User=Depends(admin_user)):
    if kind not in {"papers","jobs"}: raise HTTPException(400,"kind must be papers or jobs")
    if not file.filename.lower().endswith(".csv"): raise HTTPException(400,"Upload a CSV file")
    try: rows=list(csv.DictReader(io.StringIO((await file.read()).decode("utf-8-sig"))))
    except Exception as e: raise HTTPException(400,"Could not read CSV as UTF-8") from e
    required={"papers":{"title"},"jobs":{"title","skills"}}[kind]
    missing=required-set(rows[0].keys() if rows else [])
    if missing: raise HTTPException(400,"Missing columns: "+", ".join(sorted(missing)))
    errors=[]; imported=0
    for i,row in enumerate(rows,2):
        try:
            if not row.get("title"," ").strip(): raise ValueError("title is required")
            if kind=="papers":
                doi=(row.get("doi") or "").strip() or None
                if doi and db.query(Paper).filter(Paper.doi==doi).first(): raise ValueError("duplicate DOI")
                year=int(row["year"]) if row.get("year") else None
                save_paper(db,{"title":row["title"].strip(),"abstract":row.get("abstract",""),"year":year,"venue":row.get("venue",""),"doi":doi,"citations":int(row.get("citations") or 0),"url":row.get("url",""),"domain":row.get("domain","Other"),"authors":[x.strip() for x in row.get("authors","").split(";") if x.strip()],"topics":[x.strip() for x in row.get("topics","").split(";") if x.strip()]})
            else:
                db.add(JobPosting(title=row["title"],company=row.get("company") or "Imported",location=row.get("location") or "Not specified",skills=row["skills"],experience=row.get("experience","Not specified"),salary=row.get("salary",""),is_sample=True)); db.commit()
            imported+=1
        except Exception as e:
            db.rollback(); errors.append({"row":i,"error":str(e)})
    return {"imported":imported,"failed":len(errors),"errors":errors[:100],"is_sample":True}
@app.get(api+"/admin/stats")
def admin_stats(db:Session=Depends(get_db),admin:User=Depends(admin_user)):
    return {"users":db.query(User).count(),"papers":db.query(Paper).count(),"topics":db.query(Topic).count(),"jobs":db.query(JobPosting).count()}
