import json

from fastapi import FastAPI, Request, Form
from fastapi import Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from admin import session_make, verify_hash, take_logpswd, update_bd_text, update_bd_keys, display_allbd

CASH_TEXT = session_make()

template = Jinja2Templates(directory="templates")

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key="SECRET_KEY",  # Ключ для подписи куки
    max_age=10000,            # Время жизни куки в секундах (здесь 24 часа)
    same_site="lax",          # Защита от CSRF-атак
    https_only=False          # На продакшене True
)

data_admin = {
			'log': 'admin',
			'paswd': '12345'
}


@app.get("/home")
async def main_page(request: Request):
	return template.TemplateResponse(
									request=request,
	 								name ="main_page.html",
	 								context={"doc": CASH_TEXT}
	 								)

@app.get("/admin")
async def admin_page(request: Request):
	if request.session.get('is_admin'):
		return template.TemplateResponse(
										request=request,
										name='admin.html',
										context={
												"logs":logs(),
												"allbd": display_allbd(CASH_TEXT)
												}
										)
	else: return template.TemplateResponse(request=request,
								 name='login_form.html')

@app.post("/admin")
async def post_db_def(
	request: Request,
	change_text: str | None = Form(None),
	textname: str | None = Form(None),
	firstkey: str | None = Form(None),
	seckey: str | None = Form(None),
	new_text: str | None = Form(None),
			):
	print(firstkey, seckey, new_text)
	log, hash_paswd = take_logpswd()
	sess_pswd = request.session.get('passwd')
	sess_log = request.session.get('login')
	global CASH_TEXT
	if verify_hash(hash_paswd, sess_pswd) \
		and log != sess_log:
		print('авторизация не пройдена')
		return template.TemplateResponse(
										request=request,
										name='login.html'
			)

	request.session['is_admin'] = True
	
	if firstkey and seckey and new_text:
		print('/admin post')
		update_bd_keys(CASH_TEXT, firstkey, seckey, new_text)
		return template.TemplateResponse(
										request=request,
										name='admin.html',
										context={
												"logs":logs(),
												"allbd": display_allbd(CASH_TEXT)
												}
										)

	elif change_text and textname:
		update_bd_text(CASH_TEXT, textname, change_text)
		return template.TemplateResponse(
										request=request,
										name='admin.html',
										context={
												"logs":logs(),
												"allbd": display_allbd(CASH_TEXT)
												}
										)
	
	print('pizda PIZDAAAA /admin.post')
	return template.TemplateResponse(
									request=request,
									name='admin.html',
									context={
											"logs":logs(),
											"allbd": display_allbd(CASH_TEXT)
											}
									)


@app.post('/login')
async def login(request: Request,
				login: str = Form(),
				passwd: str = Form()):
	request.session['passwd'] = passwd
	request.session['login'] = login
	log, hash_paswd = take_logpswd()
	if verify_hash(hash_paswd, request.session.get('passwd')) \
		and log == request.session.get('login'):
			request.session['is_admin'] = True
			return RedirectResponse(url = '/admin', status_code=303)

	return template.TemplateResponse(
									request=request,
									name='login_form.html'
									)

@app.get('/login')
async def login_form(request: Request):
	log, hash_paswd = take_logpswd()
	if verify_hash(hash_paswd, request.session.get('passwd')) \
		and log == request.session.get('login'):
			request.session['is_admin'] = True
			return RedirectResponse(url = '/admin', status_code=303)

	else: return template.TemplateResponse(
									request=request,
									name='login_form.html'
									)


def logs():
	with open('logs.txt', 'r', encoding='utf-8') as f:
		r = f.read()
		return r

