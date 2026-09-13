from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError


import json, time


from sqlalchemy import create_engine, Column, Integer, String, select

from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class TEXTS(Base):
	__tablename__ = "table_texts"


	id = Column(Integer, primary_key=True)
	tag = Column(String)
	text = Column(String)

class ADMIN(Base):
    __tablename__ = 'admin_table'

    id = Column(Integer, primary_key=True)
    login = Column(String)
    passwd = Column(String)


DATABASE_URL = "postgresql://postgres:8841@localhost:5432/new_base_db"

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()



session.close()


def session_make():
	doc = {}
	with Session() as session:
		query = select(TEXTS.id, TEXTS.tag, TEXTS.text)

		res = session.execute(query).mappings().all()
		for i in res:
			tag = i["tag"]
			text = i["text"]
			doc[tag] = json.loads(text)

	return doc



def update_bd_text(cash_table, search_text: str, new_value: str):
	search_text = search_text.lower()
	for tag, content in cash_table.items():
		for key, value in  content.items():
			if search_text in value:
				with Session() as session:
					query = select(TEXTS).where(TEXTS.tag == tag)
					res = session.scalars(query).first()

					data_dict = json.loads(res.text)

					old_value = data_dict[key]

					data_dict[key] = new_value

					res.text = json.dumps(data_dict, ensure_ascii=False)

					session.commit()

					cash_table[tag][key] = new_value

					write_logs(old_value, new_value)

					

def update_bd_keys(cash_table, keyone: str, seckey: str, new_value: str):
    query = select(TEXTS).where(TEXTS.tag == keyone)
    with Session() as session:
        res_texts = session.scalars(query).first()
        dict_texts = json.loads(res_texts.text)
        old_value = dict_texts[f'{seckey}']
        dict_texts[f'{seckey}'] = new_value
        res_texts.text = json.dumps(dict_texts, ensure_ascii=False)
        cash_table[keyone][seckey] = new_value
        session.commit()
        write_logs(old_value, new_value)



					
def display_allbd(cash_table):
    all_bd = []
    for base_key, data in cash_table.items():
        for key, value in data.items():
            result = {
                    'firstkey': base_key,
                    'seckey': key,
                    'value': value 
                    }
            all_bd.append(result)

    return all_bd


def take_logpswd(): 
    query = select(ADMIN).where(ADMIN.login == 'admin')
    with Session() as session:
        res = session.scalars(query).first()

    return res.login, res.passwd


def verify_hash(hash_str, passwd):
    ph = PasswordHasher()
    try:
        return ph.verify(hash_str, passwd)
    except (VerifyMismatchError, InvalidHashError):
        print('vetify hash error')
        return False


def write_logs(old_value, new_value):
	with open('logs.txt', 'a', encoding='utf-8') as f:
		local_time = time.localtime()
		res_time = time.strftime('%d.%m.%Y %H:%M', local_time)
		f.write(
			f'время изменения: {res_time} старое значение: {old_value}, изменено на: {new_value}\n\n\n'
			)
