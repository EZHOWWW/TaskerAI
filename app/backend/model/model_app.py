from fastapi import FastAPI, Depends, HTTPException
from backend.model.model import TaskerModel
from backend.model.imodel import ModelRequest

app = FastAPI()


def get_tasker_model():
    return TaskerModel()


@app.get("/model/promt")
async def promt(req: ModelRequest, model: TaskerModel = Depends(get_tasker_model)):
    try:
        res = model.promt(req.system_promt, req.user_promt)
        return res
    except Exception as e:
        raise HTTPException(500, str(e))
