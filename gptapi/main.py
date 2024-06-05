import openai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
from pymongo import MongoClient

# OpenAI API 키 설정
openai.api_key = 'sk-proj-E2GE5qwuGArn5XIkInB7T3BlbkFJiJuegxYFp8pwMDQ7QDeM'

app = FastAPI()

# MongoDB 연결 설정
client = MongoClient('mongodb+srv://kingju232:oqF6WeMlIzGSAhqQ@cluster0.yelhicb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['aiproject']
collection = db['ads']

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdGenerator:
    def __init__(self, engine='gpt-3.5-turbo'):
        self.engine = engine

    def using_engine(self, prompt):
        system_instruction = 'You are an assistant that helps in writing marketing copy. Create marketing copy based on the user\'s content.'
        messages = [{'role': 'system', 'content': system_instruction},
                    {'role': 'user', 'content': prompt}]
        try:
            response = openai.ChatCompletion.create(
                model=self.engine,
                messages=messages
            )
            result = response.choices[0].message['content'].strip()
            return result
        except Exception as e:
            logger.error(f"OpenAI API 호출 중 오류 발생: {e}")
            raise HTTPException(status_code=500, detail="OpenAI API 호출 중 오류 발생")

    def generate(self, product_name, details, tone_and_manner):
        prompt = f'Product Name: {product_name}\nDetails: {details}\nTone and Manner: {tone_and_manner}\nCreate marketing copy based on the above content.'
        result = self.using_engine(prompt=prompt)
        return result


class Product(BaseModel):
    product_name: str
    details: str
    tone_and_manner: str


@app.post('/create_ad')
async def create_ad(product: Product):
    ad_generator = AdGenerator()
    try:
        ad = ad_generator.generate(product_name=product.product_name,
                                   details=product.details,
                                   tone_and_manner=product.tone_and_manner)

        # MongoDB에 데이터 저장
        collection.insert_one({
            "product_name": product.product_name,
            "details": product.details,
            "tone_and_manner": product.tone_and_manner,
            "ad": ad
        })
        return {'ad': ad}
    except Exception as e:
        logger.error(f"광고 문구 생성 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail="광고 문구 생성 중 오류 발생")

