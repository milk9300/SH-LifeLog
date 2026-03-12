from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import crud, models, schemas
from ..core.database import get_db
from ..crud import article as crud_article

router = APIRouter()

@router.post("/", response_model=schemas.Problem)
def create_problem(problem: schemas.ProblemCreate, db: Session = Depends(get_db)):
    return crud.problem.create_problem(db=db, problem=problem)

@router.get("/", response_model=List[schemas.Problem])
def read_problems(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    problems = crud.problem.get_problems(db, skip=skip, limit=limit)
    return problems

@router.get("/{problem_id}", response_model=schemas.Problem)
def read_problem(problem_id: int, db: Session = Depends(get_db)):
    db_problem = crud.problem.get_problem(db, problem_id=problem_id)
    if db_problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    return db_problem

@router.put("/{problem_id}", response_model=schemas.Problem)
def update_problem(problem_id: int, problem: schemas.ProblemUpdate, db: Session = Depends(get_db)):
    db_problem = crud.problem.update_problem(db, problem_id=problem_id, problem=problem)
    if db_problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    return db_problem

@router.delete("/{problem_id}", response_model=schemas.Problem)
def delete_problem(problem_id: int, db: Session = Depends(get_db)):
    db_problem = crud.problem.delete_problem(db, problem_id=problem_id)
    if db_problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    return db_problem


# ---------- 问题记录 → 技术文章 ----------
@router.post("/{problem_id}/generate-article", response_model=schemas.Article)
def generate_article_from_problem(problem_id: int, request: schemas.ArticleGenerateRequest = None, db: Session = Depends(get_db)):
    """将知识沉淀中的问题记录生成为技术文章草稿，进入文章编辑流程"""
    db_problem = crud.problem.get_problem(db, problem_id=problem_id)
    if db_problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")

    # 如果向导提供了完整内容，则直接使用；否则使用默认模板
    content = ""
    if request and request.content:
        content = request.content
    else:
        # 组装 Markdown 格式的文章默认模板
        content = f"# {db_problem.title}\n\n"
        content += "## 背景\n\n"
        if db_problem.description:
            content += f"{db_problem.description}\n\n"
        content += "## 原因分析\n\n"
        content += "<!-- 在此分析问题的根因 -->\n\n"
        content += "## 解决方案\n\n"
        content += "<!-- 在此记录解决方案 -->\n\n"
        content += "## 总结\n\n"
        content += "<!-- 总结知识要点 -->\n"

    article_data = schemas.ArticleCreate(
        title=db_problem.title,
        content=content,
        category="technical",
        status="draft",
        tags="知识沉淀",
        problem_id=db_problem.id,
        project_id=db_problem.project_id
    )
    db_article = crud_article.create_article(db=db, article=article_data)
    
    # 将生成的文章 ID 关联回问题记录
    crud.problem.update_problem(db, problem_id=problem_id, problem=schemas.ProblemUpdate(article_id=db_article.id))
    
    return db_article


# ---------- AI Copilot 助手 ----------
from openai import OpenAI
from ..core import config

client = OpenAI(
    api_key=config.AI_API_KEY,
    base_url=config.AI_BASE_URL
)

STEP_PROMPTS = {
    1: "你是一个技术专家，正在协助用户【还原案发现场】。请根据用户提供的问题标题和背景信息，分析可能的错误原因，并提示用户补充遗漏的关键信息（如具体的报错日志、环境配置等）。",
    2: "你是一个技术专家，正在协助用户进行【探索式排查】。请根据目前的背景和排查现状，给出下一步的排查建议和思维模型，引导用户记录关键的尝试过程。",
    3: "你是一个技术专家，正在协助用户进行【解决方案提炼】。请协助用户总结问题的核心解决方案，并指导用户如何编写高质量、可复用的代码片段或配置项。",
    4: "你是一个技术专家，正在协助用户进行【知识升华】。请引导用户思考问题的根源和预防方案，并将整个过程提炼为一篇高质量的技术文章要点。"
}

@router.post("/{problem_id}/ai-assist", response_model=schemas.AIAssistResponse)
def ai_assist_problem(problem_id: int, request: schemas.AIAssistRequest, db: Session = Depends(get_db)):
    """AI Copilot 协助用户完成知识沉淀的各个步骤"""
    db_problem = crud.problem.get_problem(db, problem_id=problem_id)
    if db_problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")

    system_prompt = STEP_PROMPTS.get(request.step, "你是一个技术专家，正在协助用户整理技术问题。")
    
    # 构造对话上下文
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"当前问题标题：{db_problem.title}\n初始描述：{db_problem.description}\n当前步骤上下文数据：{request.context}\n用户追问：{request.user_input or '请给我一些建议'}"}
    ]

    try:
        response = client.chat.completions.create(
            model=config.AI_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        reply = response.choices[0].message.content
        
        # 简单提取建议（假设 AI 会给出一些关键点）
        # 这里可以根据返回内容进行正则匹配提取更结构化的 suggestions
        suggestions = ["补充环境信息", "检查依赖版本", "查看堆栈信息"] if request.step == 1 else None
        
        return schemas.AIAssistResponse(reply=reply, suggestions=suggestions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI Service Error: {str(e)}")
