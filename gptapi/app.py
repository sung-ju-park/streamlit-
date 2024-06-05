import streamlit as st
import requests
import pymongo
import pandas as pd

# MongoDB 연결 설정
mongo_client = pymongo.MongoClient('mongodb+srv://kingju232:oqF6WeMlIzGSAhqQ@cluster0.yelhicb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = mongo_client['aiproject']
collection = db['ads']

# Streamlit 애플리케이션 설정
st.title('광고 문구 서비스앱')
generate_ad_url = 'http://127.0.0.1:8000/create_ad'

# 입력 폼 생성
product_name = st.text_input('제품 이름')
details = st.text_input('주요 내용')
options = st.multiselect('광고 문구의 느낌', options=['기본', '재밌게', '차분하게', '과장스럽게', '참신하게', '고급스럽게'], default=['기본'])

# 광고 문구 생성 버튼
if st.button("광고 문구 생성하기"):
    try:
        response = requests.post(
            generate_ad_url,
            json={"product_name": product_name,
                  "details": details,
                  "tone_and_manner": ", ".join(options)}
        )
        response.raise_for_status()
        ad_text = response.json().get('ad', 'No ad text returned')

        st.success(ad_text)
    except requests.exceptions.RequestException as e:
        st.error(f"연결 실패: {e}")
    except ValueError as e:
        st.error(f"응답을 처리하는 동안 오류 발생: {e}")
    except Exception as e:
        st.error(f"예기치 않은 오류 발생: {e}")

# MongoDB에서 데이터 가져와서 DataFrame으로 변환
ads = list(collection.find({}, {"_id": 0, "product_name": 1, "details": 1, "tone_and_manner": 1, "ad": 1}))
df = pd.DataFrame(ads)

# 데이터가 있을 경우 표로 표시
if not df.empty:
    st.subheader("생성된 광고 문구")
    st.dataframe(df)