from ultralytics import YOLO
import gradio as gr
import cv2
import numpy as np
pistol_model = YOLO("yolov8l-worldv2.pt")
pistol_model.set_classes(["pistol", "gun", "handgun", "firearm"])
knife_model = YOLO("yolov8l-worldv2.pt")
knife_model.set_classes(["knife"])
login_ok = False
def login(user, pwd):
    global login_ok
    if user == "Lovina" and pwd == "1234":
        login_ok = True
        return "Login success", gr.update(visible=False), gr.update(visible=True)
    else:
        login_ok = False
        return "Wrong login", gr.update(visible=True), gr.update(visible=False)
def logout():
    global login_ok
    login_ok = False
    return "Logged out", gr.update(visible=True), gr.update(visible=False), None, None, ""
def red_filter(img):
    red_layer = np.full_like(img, (0, 0, 255), dtype=np.uint8)
    out = cv2.addWeighted(img, 0.6, red_layer, 0.4, 0)
    return out
def detect(img):
    if login_ok == False:
        return None, "Please login first"
    if img is None:
        return None, "Upload image"
    p = pistol_model(img, conf=0.05, verbose=False)
    k = knife_model(img, conf=0.05, verbose=False)
    if len(p[0].boxes) > 0:
        result = p[0].plot()
        result = red_filter(result)
        return result, "THREAT DETECTED - PISTOL FOUND"
    if len(k[0].boxes) > 0:
        result = k[0].plot()
        result = red_filter(result)
        return result, "THREAT DETECTED - KNIFE FOUND"
    return img, "SAFE - No harmful object"
with gr.Blocks() as app:
    gr.Markdown("Security System - Harmful Object Detection")
    gr.Markdown("By Lovina Koropa")
    with gr.Column(visible=True) as login_box:
        gr.Markdown("Login")
        u = gr.Textbox(label="Username", value="Lovina")
        pw = gr.Textbox(label="Password", type="password", value="1234")
        btn1 = gr.Button("Login")
        st = gr.Textbox(label="Status")
    with gr.Column(visible=False) as detect_box:
        gr.Markdown("Detection")
        inp = gr.Image(type="numpy", label="Upload image")
        out = gr.Image(label="Result")
        txt = gr.Textbox(label="Output")
        with gr.Row():
            btn2 = gr.Button("Scan")
            btn3 = gr.Button("Logout")
    btn1.click(login, [u, pw], [st, login_box, detect_box])
    btn2.click(detect, inp, [out, txt])
    btn3.click(logout, None, [st, login_box, detect_box, inp, out, txt])
app.launch()
