"""Load clearly labeled demonstration records into an empty database."""
from app.database import Base, engine, SessionLocal
from app.models import Paper, Topic, PaperTopic, Author, PaperAuthor, JobPosting
from app.services import save_paper

Base.metadata.create_all(engine)
db=SessionLocal()
if db.query(Paper).count()==0:
    records=[
      ("Attention Is All You Need",2017,"Natural Language Processing",125000,"Neural machine translation architecture based entirely on attention mechanisms."),
      ("BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",2019,"Natural Language Processing",95000,"Pre-training deep bidirectional representations from unlabeled text."),
      ("Language Models are Few-Shot Learners",2020,"Generative AI",22000,"Scaling language models enables few-shot task adaptation."),
      ("An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale",2021,"Computer Vision",18000,"Applying a pure transformer directly to image patches for classification."),
      ("Training language models to follow instructions with human feedback",2022,"Generative AI",11000,"Instruction tuning and preference learning improve language model usefulness."),
      ("Highly accurate protein structure prediction with AlphaFold",2021,"Computational Biology",16000,"A machine learning system predicts protein structures with high accuracy."),
      ("Deep Residual Learning for Image Recognition",2016,"Computer Vision",105000,"Residual connections enable training substantially deeper neural networks."),
      ("A Survey of Large Language Models",2023,"Generative AI",5200,"A survey of pre-training, adaptation, evaluation, and applications of large language models."),
      ("Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks",2020,"Natural Language Processing",8500,"Combines parametric generation with retrieval from a dense vector index."),
      ("Denoising Diffusion Probabilistic Models",2020,"Generative AI",9800,"A diffusion probabilistic model learns to generate data by reversing a noise process."),
      ("Adam: A Method for Stochastic Optimization",2015,"Optimization",90000,"An adaptive stochastic optimization method based on first and second moments."),
      ("Mastering the game of Go with deep neural networks and tree search",2016,"Reinforcement Learning",14000,"Combines policy and value networks with Monte Carlo tree search."),
      ("A Gentle Introduction to Graph Neural Networks",2021,"Graph Machine Learning",650,"Overview of message passing and graph representation learning."),
      ("Federated Learning: Challenges, Methods, and Future Directions",2020,"Privacy-Preserving AI",4800,"Reviews collaborative model training while keeping data decentralized."),
      ("Deep Learning for Medical Image Analysis: A Survey",2017,"Medical AI",4300,"Survey of deep learning methods for medical image analysis."),
      ("XGBoost: A Scalable Tree Boosting System",2016,"Machine Learning",34000,"Scalable end-to-end tree boosting system for machine learning."),
      ("The Rise and Potential of Large Language Model Based Agents",2023,"AI Agents",3000,"Survey of autonomous agents built with large language models."),
      ("Data-Efficient Image Transformers and Distillation through Attention",2021,"Computer Vision",5700,"Data-efficient image transformer training with distillation."),
      ("Computer Vision for Autonomous Vehicles: Problems, Datasets and State of the Art",2022,"Computer Vision",900,"Review of perception methods and datasets for autonomous driving."),
      ("A Survey on Explainable Artificial Intelligence",2020,"Explainable AI",6200,"Reviews methods that make machine learning decisions more interpretable.")]
    for title,year,topic,citations,abstract in records:
        save_paper(db,{"title":title,"year":year,"domain":topic,"citations":citations,"abstract":abstract,"venue":"Demonstration catalogue","doi":None,"url":"","authors":["Tracker Demo Research Group"],"topics":[topic]})
    for skill,title,location in [("Python, Machine Learning, NLP","Machine Learning Engineer","Bengaluru"),("Python, SQL, Data Science","Data Scientist","Hyderabad"),("React, Node.js, AWS","Full Stack Engineer","Remote"),("Python, AI, Docker","AI Engineer","Pune"),("Java, SQL, Kubernetes","Backend Engineer","Chennai"),("Python, NLP, Transformers","NLP Research Engineer","Remote"),("C#, Azure, SQL","Cloud Software Engineer","Mumbai"),("Python, PyTorch, Machine Learning","Computer Vision Engineer","Bengaluru")]:
        db.add(JobPosting(title=title,company="Illustrative Sample Co.",location=location,skills=skill,is_sample=True,posting_date="2026-01-01"))
    db.commit()
if db.query(JobPosting).count()<100:
    # Plausible but fictional job listings for dashboard behavior; every row stays flagged as sample.
    role_skills=[
      ("Machine Learning Engineer","Python, Machine Learning, PyTorch, SQL"),
      ("AI Engineer","Python, AI, Machine Learning, Docker"),
      ("NLP Engineer","Python, NLP, Transformers, Machine Learning"),
      ("Data Scientist","Python, SQL, Data Science, Machine Learning"),
      ("Data Engineer","Python, SQL, AWS, Docker"),
      ("Backend Engineer","Java, SQL, Docker, Kubernetes"),
      ("Full Stack Engineer","React, Node.js, SQL, AWS"),
      ("Frontend Engineer","React, JavaScript, Node.js"),
      ("Cloud Engineer","AWS, Azure, Docker, Kubernetes"),
      ("DevOps Engineer","AWS, Docker, Kubernetes, Python"),
      ("MLOps Engineer","Python, Machine Learning, AWS, Kubernetes"),
      ("Computer Vision Engineer","Python, PyTorch, Machine Learning, OpenCV"),
      ("Research Engineer, LLMs","Python, NLP, Transformers, PyTorch"),
      ("Database Developer","SQL, Python, Azure"),
      ("Software Engineer, C#","C#, Azure, SQL, Docker"),
      ("Software Engineer, Java","Java, SQL, Kubernetes"),
      ("Business Intelligence Analyst","SQL, Data Science, Python"),
      ("Security Analyst","Python, AWS, SQL, Kubernetes"),
      ("Robotics Engineer","Python, Machine Learning, C++, Docker"),
      ("Platform Engineer","Kubernetes, Docker, AWS, Python"),
    ]
    locations=["Bengaluru","Hyderabad","Pune","Chennai","Remote"]
    companies=["Sample Systems Lab","Illustrative Cloud Works","Demo Analytics Group","Example Technology Studio","Fictional Research Computing"]
    years=["0–2 years","2–4 years","3–5 years","1–3 years","2–5 years"]
    for role_index,(title,skills) in enumerate(role_skills):
        for location_index,location in enumerate(locations):
            db.add(JobPosting(title=title,company=companies[location_index],location=location,experience=years[(role_index+location_index)%len(years)],salary="Illustrative range only",skills=skills,employment_type="Full-time",posting_date=f"2026-{(role_index%12)+1:02d}-01",is_sample=True))
    db.commit()
db.close()
print("Seed complete. These records are illustrative demonstration data, not verified live records.")
