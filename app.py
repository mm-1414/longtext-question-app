import streamlit as st
import openai
import hashlib
import sqlite3

# OpenAI APIキーをSecretsから読み込む
openai.api_key = st.secrets["OPENAI_API_KEY"]

def generate_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()

def is_duplicate(text):
    hash_value = generate_hash(text)
    conn = sqlite3.connect("used_texts.db")
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS used (hash TEXT PRIMARY KEY)')
    c.execute('SELECT hash FROM used WHERE hash = ?', (hash_value,))
    exists = c.fetchone()
    if not exists:
        c.execute('INSERT INTO used (hash) VALUES (?)', (hash_value,))
        conn.commit()
        conn.close()
        return False
    conn.close()
    return True

st.title("自動長文問題作成アプリ（大学受験向け）")
text = st.text_area("英語の長文を貼り付けてください", height=300)

if st.button("問題を生成"):
    if text.strip() == "":
        st.warning("まずは英文を入力してください。")
    else:
        duplicate = is_duplicate(text)
        variation_note = "※この長文は以前使用されたため、問題形式を少し変更しています。" if duplicate else ""

        prompt = f"""
以下の英文をもとに、以下の5種類の読解問題を作成してください。
※各問題のあとに答えと解説は書かないでください。
※すべての「問題」は上にまとめて、「答えと解説」は一番下にまとめてください。
※同じ長文が入力された場合、出題形式や出題箇所を変更してください。

【出題する問題】
1. 空所補充問題（文中の単語を1つ空欄にする）
2. 下線部和訳問題（訳すべき文を下線付きで表示）
3. 指示語の内容説明問題（指示語とその内容を問う）
4. 英訳問題（日本語文を英訳）
5. 内容一致問題（選択肢5つで、正解は2つ）

【出力形式】
上半分：問題のみ
下半分：すべての問題に対する「解答と簡潔な解説（1〜2文）」

英文：
{text}

形式に従って、問題→解答・解説の順で出力してください。
"""

        with st.spinner("問題を生成中..."):
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            output = response.choices[0].message['content']
            st.success("問題が生成されました！")
            if variation_note:
                st.markdown(f"##### {variation_note}")
            st.markdown(output)
