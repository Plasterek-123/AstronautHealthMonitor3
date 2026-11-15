"""Small offline document-finding chat; no generated treatment advice."""
import re
import flet as ft
from config import txt,WHITE,GRAY,CYAN,CARD,BORDER

def matching_articles(query,articles):
    terms=set(re.findall(r'[a-z0-9]+',query.lower()))-{'a','the','is','how','to','what','i','my','and','for','of'}
    aliases={'heart':'ecg','pulse':'bpm','breathing':'spo2','radiation':'dosimeter','resuscitation':'cpr'}
    terms|={aliases[t] for t in list(terms) if t in aliases}
    ranked=[]
    for article in articles:
        title=(article['title']+' '+' '.join(article.get('tags',[]))).lower()
        body=(article['summary']+' '+article['content']).lower()
        score=sum(3*(term in title)+(term in body) for term in terms)
        if score:ranked.append((score,article))
    return [a for _,a in sorted(ranked,key=lambda item:item[0],reverse=True)[:2]]

def build_guide_assistant(get_articles,on_article,page=None):
    messages=ft.Column(spacing=6,scroll=ft.ScrollMode.AUTO,expand=True,auto_scroll=True,
        controls=[txt('Ask for a topic, e.g. ECG, radiation or CPR. I can find local Guidebook articles.',12,GRAY)])
    entry=ft.TextField(hint_text='Find a procedure or topic…',dense=True,expand=True)
    panel=ft.Container(visible=False,height=225,padding=12,bgcolor=CARD,border_radius=12,
        border=ft.Border.all(1,BORDER))
    def update():
        if page is not None:page.update()
    def send(e=None):
        query=(entry.value or '').strip()
        if not query:return
        entry.value='';messages.controls.append(txt('You: '+query,12,WHITE))
        matches=matching_articles(query,get_articles())
        messages.controls.append(txt('Guide assistant: '+('I found these local documents:' if matches else 'No matching article. Try a metric or procedure name, or browse the chapters.'),12,CYAN))
        for art in matches:
            messages.controls.append(ft.TextButton(content=art['title'],on_click=lambda e,a=art:on_article(a)))
        messages.controls=messages.controls[-18:];update()
    def toggle(e):
        panel.visible=not panel.visible;update()
    entry.on_submit=send
    panel.content=ft.Column(spacing=6,controls=[txt('Offline CDSS demo · document search only, no diagnosis',10,GRAY),messages,
        ft.Row(controls=[entry,ft.IconButton(icon=ft.Icons.SEND,tooltip='Send',on_click=send)])])
    return ft.Column(spacing=6,controls=[ft.TextButton(content='CDSS · Guide assistant',icon=ft.Icons.CHAT_BUBBLE_OUTLINE,on_click=toggle),panel])
