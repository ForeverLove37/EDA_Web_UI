from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
import pandas as pd
from ydata_profiling import ProfileReport
import sweetviz as sv
import io
import matplotlib.pyplot as plt
import base64
from llm.services import llm_client

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/api/eda/conventional", response_class=HTMLResponse)
async def conventional_eda(file: UploadFile = File(...), tool: str = Form(...)):
    try:
        df = pd.read_csv(file.file)
    except Exception as e:
        return f"<html><body><h1>Error reading file</h1><p>{e}</p></body></html>"

    if tool == "ydata-profiling":
        profile = ProfileReport(df, title="Pandas Profiling Report")
        return profile.to_html()
    elif tool == "sweetviz":
        report = sv.analyze(df)
        return report.to_html()
    elif tool == "custom_plot":
        fig, ax = plt.subplots()
        df.iloc[:, 0].hist(ax=ax)
        
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        
        return f'<html><body><h1>Custom Plot</h1><img src="data:image/png;base64,{img_str}"/></body></html>'
    else:
        return "<html><body><h1>Invalid tool selected</h1></body></html>"

@app.post("/api/eda/ai/analyze", response_class=JSONResponse)
async def ai_analyze(file: UploadFile = File(...), llm_choice: str = Form(...)):
    content = await file.read()
    text_data = content.decode('utf-8')
    result = await llm_client.analyze_data(llm_choice, text_data)
    return result

@app.post("/api/eda/ai/transform", response_class=JSONResponse)
async def ai_transform(file: UploadFile = File(...), llm_choice: str = Form(...), transformation_prompt: str = Form(...)):
    content = await file.read()
    text_data = content.decode('utf-8')
    result = await llm_client.transform_data(llm_choice, text_data, transformation_prompt)
    return result
