import streamlit as st
import json
import os
import re
from pathlib import Path

st.set_page_config(
    page_title="土地活用 単語帳",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="collapsed"
)

BUILT_IN_CARDS = [
    {"id": 1, "category": "建築・法規", "term": "用途地域", "reading": "ようとちいき", "meaning": "都市計画法で定められた土地の使い方のルール。住居系・商業系・工業系など13種類あり、建てられる建物の種類や規模が決まる。", "example": "「この土地は第一種低層住居専用地域なので、アパートは2階建てまで」"},
    {"id": 2, "category": "建築・法規", "term": "建蔽率", "reading": "けんぺいりつ", "meaning": "敷地面積に対して建物が占めてよい面積の割合（%）。60%なら100㎡の土地に最大60㎡の建物が建てられる。", "example": "「建蔽率60%・容積率200%の土地です」"},
    {"id": 3, "category": "建築・法規", "term": "容積率", "reading": "ようせきりつ", "meaning": "敷地面積に対して建物の延べ床面積の割合（%）。数字が大きいほど高い・大きな建物が建てられる。", "example": "「容積率200%なら100㎡の土地に延べ200㎡の建物が建てられる」"},
    {"id": 4, "category": "建築・法規", "term": "道路斜線制限", "reading": "どうろしゃせんせいげん", "meaning": "前面道路の幅に応じて建物の高さを制限するルール。道路から離れるほど高くできる。", "example": "「道路幅4mだと近いところは8m以上の高さが出せない」"},
    {"id": 5, "category": "建築・法規", "term": "北側斜線制限", "reading": "きたがわしゃせんせいげん", "meaning": "北隣の土地の日当たりを守るために建物の高さを制限するルール。主に住居系の用途地域に適用される。", "example": "「1・2低層と中高層の住居地域で北側斜線がかかる」"},
    {"id": 6, "category": "建築・法規", "term": "接道義務", "reading": "せつどうぎむ", "meaning": "建物を建てるには、幅4m以上の道路に2m以上接していないといけないルール。", "example": "「再建築不可物件は接道義務を満たしていない」"},
    {"id": 7, "category": "建築・法規", "term": "セットバック", "reading": "せっとばっく", "meaning": "道路幅が4m未満の場合、道路中心線から2m後退した位置を敷地境界とみなすこと。", "example": "「この土地は3m道路なのでセットバックが50cm必要」"},
    {"id": 8, "category": "建築・法規", "term": "再建築不可", "reading": "さいけんちくふか", "meaning": "今ある建物を壊して新しい建物を建てられない土地のこと。接道義務を満たしていないケースが多い。", "example": "「再建築不可物件は土地活用の提案がしにくい」"},
    {"id": 9, "category": "建築・法規", "term": "高度地区", "reading": "こうどちく", "meaning": "用途地域とは別に、建物の最高・最低高さを制限する地区。", "example": "「第1種高度地区では10mが最高高さ」"},
    {"id": 10, "category": "建築・法規", "term": "防火地域・準防火地域", "reading": "ぼうかちいき・じゅんぼうかちいき", "meaning": "火災延焼を防ぐため、建物の構造を制限するエリア。都市部の商業・住宅密集地に多い。", "example": "「準防火地域では木造でも一定の防火措置が必要」"},
    {"id": 11, "category": "不動産・登記", "term": "路線価", "reading": "ろせんか", "meaning": "国税庁が定める道路に面した土地1㎡あたりの価格。相続税・贈与税の計算に使う。", "example": "「この道路の路線価は200千円/㎡なので…」"},
    {"id": 12, "category": "不動産・登記", "term": "地目", "reading": "ちもく", "meaning": "土地の用途・種類を登記簿に記載した区分。宅地・田・畑・山林・雑種地など23種類ある。", "example": "「地目が農地のままだと農地転用が必要」"},
    {"id": 13, "category": "不動産・登記", "term": "公図", "reading": "こうず", "meaning": "法務局が管理する土地の形・境界・地番を示した地図。境界確認や測量の基本資料。", "example": "「公図で隣地との境界を確認する」"},
    {"id": 14, "category": "不動産・登記", "term": "地番", "reading": "ちばん", "meaning": "登記上の土地の番号。住所（住居表示）とは別物で、ズレていることが多い。", "example": "「住所は〇〇町1-2-3だけど、地番は〇〇町234番地」"},
    {"id": 15, "category": "不動産・登記", "term": "登記簿謄本", "reading": "とうきぼとうほん", "meaning": "土地・建物の所有者・面積・抵当権などが記載された公的な書類。現在は「登記事項証明書」が正式名称。", "example": "「土地オーナーの確認のために登記簿謄本を取得する」"},
    {"id": 16, "category": "不動産・登記", "term": "固定資産税評価額", "reading": "こていしさんぜいひょうかがく", "meaning": "市区町村が固定資産税・都市計画税の計算に使う土地・建物の評価額。実勢価格の約70%が目安。", "example": "「固定資産税評価額をベースに相続対策を考える」"},
    {"id": 17, "category": "不動産・登記", "term": "実勢価格", "reading": "じっせいかかく", "meaning": "実際に市場で売買される価格。路線価・固定資産税評価額とは異なる「本当の値段」。", "example": "「路線価は実勢価格の80%程度が目安」"},
    {"id": 18, "category": "不動産・登記", "term": "敷地面積", "reading": "しきちめんせき", "meaning": "建物を建てる土地の面積。登記上の地積と実測面積が異なることもある。", "example": "「敷地面積200㎡、容積率200%なので延べ400㎡まで建てられる」"},
    {"id": 19, "category": "営業・提案", "term": "表面利回り", "reading": "ひょうめんりまわり", "meaning": "年間賃料収入 ÷ 物件価格 × 100（%）。経費を引かない単純計算。実際より高く出るので注意。", "example": "「表面利回り8%、実質利回りは6%程度です」"},
    {"id": 20, "category": "営業・提案", "term": "実質利回り", "reading": "じっしつりまわり", "meaning": "（年間賃料収入－諸経費）÷ 物件価格 × 100（%）。管理費・修繕費・税金も引いた実態に近い数字。", "example": "「実質利回りで比較しないと正確な収益性は見えない」"},
    {"id": 21, "category": "営業・提案", "term": "土地活用", "reading": "とちかつよう", "meaning": "所有している土地を活かして収益を得ること。アパート建築・駐車場・賃貸併用住宅などが代表例。", "example": "「このまま更地にしておくと固定資産税だけかかるので土地活用を検討しませんか」"},
    {"id": 22, "category": "営業・提案", "term": "一括借上げ（サブリース）", "reading": "いっかつかりあげ", "meaning": "管理会社がオーナーから建物全体を借り上げて入居者へ転貸する仕組み。空室でもオーナーに賃料が入る。", "example": "「レオパレスの一括借上げで空室リスクを軽減できます」"},
    {"id": 23, "category": "営業・提案", "term": "融資（アパートローン）", "reading": "ゆうし", "meaning": "アパート建築費用を銀行などから借り入れること。返済計画の確認が重要。", "example": "「金融機関の融資審査が通るかどうかが重要なポイント」"},
    {"id": 24, "category": "営業・提案", "term": "相続対策", "reading": "そうぞくたいさく", "meaning": "相続税の負担を減らすための事前の取り組み。更地にアパートを建てると評価額が下がり相続税が軽減される。", "example": "「土地活用は相続対策としても有効です」"},
    {"id": 25, "category": "営業・提案", "term": "節税効果", "reading": "せつぜいこうか", "meaning": "アパート経営で経費・減価償却を活用して所得税・相続税を抑える効果。", "example": "「賃貸経営で減価償却費を計上すると節税効果があります」"},
    {"id": 26, "category": "営業・提案", "term": "減価償却", "reading": "げんかしょうきゃく", "meaning": "建物・設備の費用を耐用年数に分けて毎年経費として計上すること。現金支出なしに経費になるのがポイント。", "example": "「木造アパートは耐用年数22年で減価償却できる」"},
    {"id": 27, "category": "営業・提案", "term": "収支シミュレーション", "reading": "しゅうししみゅれーしょん", "meaning": "アパート建築後の賃料収入・ローン返済・経費などを試算して毎月の手取りや損益を計算した資料。", "example": "「収支シミュレーションを作成してオーナーに提示する」"},
    {"id": 28, "category": "営業・提案", "term": "空室率", "reading": "くうしつりつ", "meaning": "全室数のうち入居者がいない部屋の割合（%）。エリアの需要や管理の良し悪しを示す指標。", "example": "「このエリアの空室率は10%程度です」"},
    {"id": 29, "category": "社内・業界", "term": "オーナー", "reading": "おーなー", "meaning": "土地・建物の所有者のこと。レオパレスでは提案相手となる地主・家主を指す。", "example": "「このオーナーは3棟持っている」"},
    {"id": 30, "category": "社内・業界", "term": "地主", "reading": "じぬし", "meaning": "土地を所有している人。相続で引き継いだ土地を持つ地主が主な営業ターゲット。", "example": "「地主への提案では相続対策が刺さりやすい」"},
    {"id": 31, "category": "社内・業界", "term": "建築確認申請", "reading": "けんちくかくにんしんせい", "meaning": "建物を建てる前に、設計が建築基準法に合っているか自治体に確認してもらう手続き。", "example": "「建築確認が下りるまで約1ヶ月かかる」"},
    {"id": 32, "category": "社内・業界", "term": "着工・竣工", "reading": "ちゃっこう・しゅんこう", "meaning": "着工＝工事開始、竣工＝工事完了・建物完成。", "example": "「着工から竣工まで約6ヶ月」"},
    {"id": 33, "category": "社内・業界", "term": "間取り", "reading": "まどり", "meaning": "部屋の配置・広さを示した図面。1K・1LDKなどの表記で部屋の構成がわかる。", "example": "「ターゲット層に合った間取りを提案する」"},
    {"id": 34, "category": "社内・業界", "term": "更地", "reading": "さらち", "meaning": "建物がなにも建っていない土地。固定資産税の軽減措置がなく税負担が重い。", "example": "「更地のままにしておくと固定資産税が高くなる」"},
    {"id": 311, "category": "営業・提案", "term": "元利均等返済", "reading": "がんりきんとうへんさい", "meaning": "毎月の返済額（元金＋利息）が一定になる返済方式。返済計画が立てやすい。", "example": "「住宅ローンの多くは元利均等返済が採用されている」"},
    {"id": 312, "category": "営業・提案", "term": "元金均等返済", "reading": "がんきんきんとうへんさい", "meaning": "毎月の返済元金が一定になる返済方式。総利息は元利均等より少ない。", "example": "「元金均等は最初の返済額が高いが総支払いは少ない」"},
    {"id": 313, "category": "営業・提案", "term": "変動金利", "reading": "へんどうきんり", "meaning": "市場金利の変動に応じて定期的に見直される金利。低い時期は返済額が少ないがリスクがある。", "example": ""},
    {"id": 314, "category": "営業・提案", "term": "固定金利", "reading": "こていきんり", "meaning": "融資期間中ずっと金利が変わらない方式。返済額が確定するので長期計画が立てやすい。", "example": ""},
    {"id": 300, "category": "ビジネス用語", "term": "ROI", "reading": "あーるおーあい", "meaning": "投資利益率（Return on Investment）。投資額に対してどれだけの利益が出たかを示す指標。", "example": "「このアパートのROIは年8%です」"},
    {"id": 301, "category": "ビジネス用語", "term": "キャッシュフロー", "reading": "きゃっしゅふろー", "meaning": "一定期間における現金の流入と流出の差額。賃貸経営では毎月の手残り金額を指す。", "example": "「毎月のキャッシュフローがプラスになるプランを提案する」"},
    {"id": 302, "category": "ビジネス用語", "term": "インカムゲイン", "reading": "いんかむげいん", "meaning": "賃料収入など、資産を保有することで得られる継続的な収益。", "example": "「アパート経営はインカムゲインが安定している」"},
    {"id": 303, "category": "ビジネス用語", "term": "キャピタルゲイン", "reading": "きゃぴたるげいん", "meaning": "不動産を売却したときに得られる値上がり益。", "example": "「将来のキャピタルゲインも見据えた立地選定が大事」"},
    {"id": 304, "category": "ビジネス用語", "term": "出口戦略", "reading": "でぐちせんりゃく", "meaning": "投資した不動産をいつ・どのように売却するかの計画。", "example": "「出口戦略を含めた長期的な提案をする」"},
    {"id": 305, "category": "ビジネス用語", "term": "デューデリジェンス", "reading": "でゅーでりじぇんす", "meaning": "投資や取引前に行う詳細な調査・検証のこと。", "example": ""},
    {"id": 306, "category": "不動産・登記", "term": "抵当権", "reading": "ていとうけん", "meaning": "融資を受けた際に土地・建物に設定される担保権。ローン返済が滞ると競売にかけられる。", "example": ""},
    {"id": 307, "category": "不動産・登記", "term": "借地権", "reading": "しゃくちけん", "meaning": "他人の土地を借りて建物を建てる権利。地代を支払う。", "example": ""},
    {"id": 308, "category": "不動産・登記", "term": "農地転用", "reading": "のうちてんよう", "meaning": "農地を宅地など農業以外の用途に変えること。農業委員会や都道府県知事の許可が必要。", "example": ""},
    {"id": 309, "category": "不動産・登記", "term": "市街化区域", "reading": "しがいかくいき", "meaning": "すでに市街地を形成している区域、または優先的・計画的に市街化を図る区域。", "example": ""},
    {"id": 310, "category": "不動産・登記", "term": "市街化調整区域", "reading": "しがいかちょうせいくいき", "meaning": "市街化を抑制すべき区域。原則として宅地開発や建築が制限される。", "example": ""},
    {"id": 315, "category": "建築・法規", "term": "耐火構造", "reading": "たいかこうぞう", "meaning": "火災に対して一定時間以上、構造耐力・遮熱・遮炎性能を保持できる構造。", "example": ""},
    {"id": 316, "category": "建築・法規", "term": "日影規制", "reading": "ひかげきせい", "meaning": "建物が周辺に与える日影の時間を制限するルール。主に住居系の用途地域で適用される。", "example": ""},
    {"id": 317, "category": "建築・法規", "term": "地区計画", "reading": "ちくけいかく", "meaning": "一定の区域を対象に、建物の用途・高さ・壁面位置などをきめ細かく定める都市計画制度。", "example": ""},
    {"id": 318, "category": "建築・法規", "term": "長期優良住宅", "reading": "ちょうきゆうりょうじゅうたく", "meaning": "耐震性・省エネ性・劣化対策などの基準を満たした長く使える住宅。税制優遇が受けられる。", "example": ""},
]

CATEGORY_MAP = {
    "建築・法規": "建築・法規",
    "道路・接道": "建築・法規",
    "不動産・登記": "不動産・登記",
    "営業・提案": "営業・提案",
    "社内・業界": "業界・ビジネス",
    "ビジネス用語": "業界・ビジネス",
    "相続税": "税務",
    "所得税": "税務",
}

CATEGORY_COLORS = {
    "建築・法規": "#0abab5",
    "不動産・登記": "#7c3aed",
    "営業・提案": "#d97706",
    "業界・ビジネス": "#059669",
    "税務": "#e05c2a",
}

STATUS_LABELS = {"known": "わかった", "fuzzy": "曖昧", "unknown": "わからない"}
STATUS_ICONS = {"known": "●", "fuzzy": "◐", "unknown": "○"}

DATA_DIR = Path(__file__).parent / "data"
STATUSES_FILE = DATA_DIR / "statuses.json"
CUSTOM_FILE = DATA_DIR / "custom_cards.json"
DETAILS_FILE = DATA_DIR / "details.json"

def load_details():
    try:
        return json.loads(DETAILS_FILE.read_text(encoding="utf-8"))
    except:
        return {}

def load_statuses():
    try:
        return json.loads(STATUSES_FILE.read_text(encoding="utf-8"))
    except:
        return {}

def save_statuses(d):
    DATA_DIR.mkdir(exist_ok=True)
    STATUSES_FILE.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")

def load_custom():
    try:
        return json.loads(CUSTOM_FILE.read_text(encoding="utf-8"))
    except:
        return []

def save_custom(cards):
    DATA_DIR.mkdir(exist_ok=True)
    CUSTOM_FILE.write_text(json.dumps(cards, ensure_ascii=False, indent=2), encoding="utf-8")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400&family=Noto+Serif+JP:wght@400;500;600&display=swap');

* { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: "Noto Serif JP", "Hiragino Mincho ProN", Georgia, serif;
    color: #1a1a1a;
    background-color: #e8f6f5;
}
.stApp {
    background-color: #e8f6f5;
    background-image:
        url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%230abab5' fill-opacity='0.07'%3E%3Cpath d='M30 0 L60 30 L30 60 L0 30 Z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E"),
        linear-gradient(160deg, #e0f5f4 0%, #eaf8f7 40%, #d6f0ef 100%);
    min-height: 100vh;
}

/* Header */
.apple-header {
    text-align: center;
    padding: 56px 0 16px;
    border-bottom: 1px solid #e0f0ef;
    margin-bottom: 8px;
}
.apple-header h1 {
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 2.2rem;
    font-weight: 400;
    color: #1a1a1a;
    letter-spacing: 0.2em;
    margin: 0;
    text-transform: uppercase;
}
.apple-header p {
    font-size: 0.68rem;
    color: #0abab5;
    margin: 10px 0 0;
    letter-spacing: 0.35em;
    text-transform: uppercase;
}

/* Card front */
.card-front {
    background: #f0fafa;
    border-radius: 0px;
    padding: 56px 40px 44px;
    text-align: center;
    border: 1px solid #b2e0dd;
    box-shadow: none;
    min-height: 240px;
    margin-bottom: 16px;
    position: relative;
}
.card-front::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: #0abab5;
}
.category-badge {
    display: inline-block;
    font-size: 0.62rem;
    font-weight: 500;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    padding: 3px 14px;
    margin-bottom: 28px;
    border: 1px solid #0abab5;
    color: #0abab5;
    background: transparent;
}
.term-big {
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 3rem;
    font-weight: 400;
    color: #1a1a1a;
    letter-spacing: 0.04em;
    line-height: 1.1;
    margin-bottom: 12px;
}
.reading {
    font-size: 0.82rem;
    color: #888888;
    letter-spacing: 0.18em;
    margin-bottom: 16px;
}
.status-badge {
    font-size: 0.8rem;
    color: #888888;
    letter-spacing: 0.08em;
}

/* Card back */
.card-back {
    background: white;
    border-radius: 0px;
    padding: 32px 36px;
    border: 1px solid #b2e0dd;
    box-shadow: none;
    margin-bottom: 16px;
    position: relative;
}
.card-back::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: #0abab5;
}
.card-back-title {
    font-family: "Cormorant Garamond", Georgia, serif;
    font-size: 1.5rem;
    font-weight: 400;
    color: #1a1a1a;
    margin-bottom: 16px;
    letter-spacing: 0.08em;
}
.meaning {
    font-size: 0.95rem;
    color: #333333;
    line-height: 1.95;
}
.example-box {
    background: #f0fafa;
    border-left: 2px solid #0abab5;
    padding: 12px 16px;
    font-size: 0.87rem;
    color: #555555;
    margin-top: 18px;
    line-height: 1.75;
    font-style: italic;
}

/* Stat box toggle buttons */
div[data-testid="column"] div.stButton > button {
    margin-top: -8px;
    background: transparent;
    border: none;
    color: #b2e0dd;
    font-size: 0.65rem;
    padding: 2px;
    box-shadow: none;
    letter-spacing: 0;
}
div[data-testid="column"] div.stButton > button:hover {
    color: #0abab5;
    background: transparent;
}

/* Buttons */
div.stButton > button {
    font-family: "Noto Serif JP", serif;
    font-size: 0.82rem;
    font-weight: 400;
    border-radius: 0;
    padding: 12px 28px;
    border: 1px solid #1a1a1a;
    background: white;
    color: #1a1a1a;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    transition: all 0.2s;
}
div.stButton > button:hover {
    background: #1a1a1a;
    color: white;
}
div.stButton > button[kind="primary"] {
    background: #0abab5;
    color: white;
    border: 1px solid #0abab5;
    font-weight: 500;
    letter-spacing: 0.12em;
}
div.stButton > button[kind="primary"]:hover {
    background: #089e9a;
    border-color: #089e9a;
    color: white;
}

/* Tabs */
div[data-testid="stTabs"] {
    border-bottom: 1px solid #b2e0dd;
}
div[data-testid="stTabs"] button {
    font-family: "Noto Serif JP", serif;
    font-size: 0.82rem;
    font-weight: 400;
    color: #888888;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #0abab5;
    border-bottom-color: #0abab5;
}

/* Input */
div[data-testid="stSelectbox"] > div > div,
div[data-testid="stTextInput"] > div > div > input,
div[data-testid="stTextArea"] textarea {
    background: white;
    border-color: #b2e0dd;
    color: #1a1a1a;
    border-radius: 0;
    font-family: "Noto Serif JP", serif;
    font-size: 0.9rem;
}

/* Expander */
details {
    background: white;
    border-radius: 0;
    border: 1px solid #b2e0dd !important;
    box-shadow: none;
    margin-bottom: 8px;
    padding: 4px 8px;
}
summary {
    font-weight: 400;
    color: #1a1a1a;
    font-size: 0.9rem;
    letter-spacing: 0.05em;
}

/* Progress bar */
div[data-testid="stProgressBar"] > div > div {
    background: #0abab5;
    border-radius: 0;
}
div[data-testid="stProgressBar"] > div {
    background: #e0f5f4;
    border-radius: 0;
}

/* Metric */
div[data-testid="metric-container"] {
    background: #f0fafa;
    border-radius: 0;
    padding: 18px 16px;
    border: 1px solid #b2e0dd;
    box-shadow: none;
    text-align: center;
}
div[data-testid="metric-container"] label {
    font-size: 0.68rem;
    color: #888888;
    font-weight: 400;
    letter-spacing: 0.15em;
    text-transform: uppercase;
}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    font-family: "Cormorant Garamond", serif;
    font-size: 2rem;
    font-weight: 400;
    color: #0abab5;
}

/* Divider */
hr { border-color: #b2e0dd; opacity: 1; }

/* Caption / small text */
div[data-testid="stCaptionContainer"] p,
small, .stCaption {
    color: #888888 !important;
    letter-spacing: 0.08em;
}

/* Alert / info / warning */
div[data-testid="stAlert"] {
    background: #f0fafa;
    border: 1px solid #b2e0dd;
    color: #1a1a1a;
    border-radius: 0;
}
</style>
<script>
document.documentElement.setAttribute("translate", "no");
document.documentElement.setAttribute("class", "notranslate");
</script>
""", unsafe_allow_html=True)

if "show_back" not in st.session_state:
    st.session_state.show_back = False
if "card_index" not in st.session_state:
    st.session_state.card_index = 0
if "ai_result" not in st.session_state:
    st.session_state.ai_result = None
if "show_detail" not in st.session_state:
    st.session_state.show_detail = False
if "status_filter" not in st.session_state:
    st.session_state.status_filter = None
if "shuffled_ids" not in st.session_state:
    st.session_state.shuffled_ids = []
if "last_filter_key" not in st.session_state:
    st.session_state.last_filter_key = ""
if "study_cat" not in st.session_state:
    st.session_state.study_cat = "すべて"
if "study_status" not in st.session_state:
    st.session_state.study_status = "未判定"

statuses = load_statuses()
custom_cards = load_custom()
all_cards = BUILT_IN_CARDS + custom_cards
details = load_details()

def mapped_category(card):
    return CATEGORY_MAP.get(card["category"], card["category"])

def auto_category(term):
    t = term
    if any(k in t for k in ["税","相続","控除","申告","贈与","遺産","遺留","納税","課税","所得税","固定資産税","印紙税","不動産取得税","譲渡所得","租税"]):
        return "税務"
    if any(k in t for k in ["道路","接道","掘削","水道","下水","側溝","排水","放流","私道","公道","位置指定","2項","42条","43条","狭あい","セットバック","袋地","旗竿"]):
        return "道路・接道"
    if any(k in t for k in ["登記","地番","地目","公図","路線価","権利","甲区","乙区","抵当権","借地","地役権","換地","仮登記","公示価格","積算","鑑定","収益還元","取引事例","原価法","敷金","区分所有","共用","専有"]):
        return "不動産・登記"
    if any(k in t for k in ["建築","構造","基礎","耐火","斜線","用途","確認","竣工","着工","施工","防火","容積","建蔽","農地","開発","区域","地区","計画","法規","法第","法22","宅地","造成","擁壁","液状化","杭","改良","足場","配筋","外構","土間","河川","砂防","航空","文化財","生産緑地","景観","風致","港湾","国土","区画整理","減歩","換地","収用","農地法","宅地造成","急傾斜","単体規定","集団規定","不適格","通気","直張り","民法上"]):
        return "建築・法規"
    if any(k in t for k in ["利回り","節税","融資","収支","空室","サブリース","一括借上","キャッシュ","減価償却","シミュレーション","相続対策","媒介","パススルー","団体信用","ローン","金利","返済","インカム","キャピタル","出口","更地"]):
        return "営業・提案"
    if any(k in t for k in ["ROI","業者","宅建","オーナー","地主","業務停止","従業者","商業登記","法人"]):
        return "業界・ビジネス"
    return "建築・法規"

total = len(all_cards)
known_n = sum(1 for v in statuses.values() if v == "known")
fuzzy_n = sum(1 for v in statuses.values() if v == "fuzzy")
unknown_n = sum(1 for v in statuses.values() if v == "unknown")
rated = known_n + fuzzy_n + unknown_n

st.markdown("""
<div class="apple-header">
    <h1>単語帳</h1>
</div>
""", unsafe_allow_html=True)

def stat_box(col, label, value, key, status_key):
    active = st.session_state.status_filter == status_key
    bg = "#0abab5" if active else "#f0fafa"
    txt_color = "white" if active else "#888"
    num_color = "white" if active else "#0abab5"
    col.markdown(f"""
    <div style="background:{bg};border:1px solid #b2e0dd;padding:18px 16px;text-align:center;transition:all 0.2s;">
      <div style="font-size:0.68rem;color:{txt_color};letter-spacing:0.15em;" translate="no">{label}</div>
      <div style="font-family:'Cormorant Garamond',serif;font-size:2rem;font-weight:400;color:{num_color};">{value}</div>
    </div>""", unsafe_allow_html=True)
    if col.button("▼" if active else "▶", key=key, use_container_width=True):
        st.session_state.status_filter = None if st.session_state.status_filter == status_key else status_key
        st.rerun()

tab1, tab2, tab3, tab4 = st.tabs(["学習", "検索", "一覧", "追加"])

with tab1:
    import random
    cats = ["すべて"] + list(CATEGORY_COLORS.keys())
    status_opts = ["すべて", "未判定", "わからない", "曖昧", "わかった"]
    cat = st.session_state.get("study_cat", "すべて")
    status_f = st.session_state.get("study_status", "未判定")

    deck = []
    for c in all_cards:
        if cat != "すべて" and mapped_category(c) != cat:
            continue
        cid = str(c["id"])
        s = statuses.get(cid)
        if status_f == "未判定" and s is not None: continue
        if status_f == "わからない" and s != "unknown": continue
        if status_f == "曖昧" and s != "fuzzy": continue
        if status_f == "わかった" and s != "known": continue
        deck.append(c)

    # フィルターが変わったらシャッフルし直す
    filter_key = f"{cat}_{status_f}_{len(deck)}"
    if filter_key != st.session_state.last_filter_key:
        shuffled = deck[:]
        random.shuffle(shuffled)
        st.session_state.shuffled_ids = [str(c["id"]) for c in shuffled]
        st.session_state.last_filter_key = filter_key
        st.session_state.card_index = 0

    # シャッフル済み順にdeckを並べ直す
    id_to_card = {str(c["id"]): c for c in deck}
    deck = [id_to_card[i] for i in st.session_state.shuffled_ids if i in id_to_card]

    if not deck:
        st.info("このフィルターのカードはありません")
    else:
        idx = st.session_state.card_index % len(deck)
        card = deck[idx]
        cid = str(card["id"])
        cat_color = CATEGORY_COLORS.get(mapped_category(card), "#0abab5")
        current_status = statuses.get(cid)

        st.caption(f"{idx+1} / {len(deck)} 枚")
        status_txt = f"{STATUS_ICONS.get(current_status,'')} {STATUS_LABELS.get(current_status,'')}" if current_status else ""
        st.markdown(f"""
        <div class="card-front">
            <div class="category-badge" style="background:{cat_color}18;color:{cat_color};">{mapped_category(card)}</div>
            <div class="term-big">{card['term']}</div>
            <div class="reading">{card.get('reading','')}</div>
            <div class="status-badge">{status_txt}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("意味を見る" if not st.session_state.show_back else "隠す", use_container_width=True):
            st.session_state.show_back = not st.session_state.show_back
            st.rerun()

        if st.session_state.show_back:
            ex_html = f'<div class="example-box">{card["example"]}</div>' if card.get("example") else ""
            st.markdown(f"""
            <div class="card-back">
                <div class="card-back-title">{card['term']}</div>
                <div class="meaning">{card['meaning']}</div>
                {ex_html}
            </div>
            """, unsafe_allow_html=True)
            st.write("")
            b1, b2, b3 = st.columns(3)
            if b1.button("わからない", use_container_width=True):
                statuses[cid] = "unknown"; save_statuses(statuses)
                st.session_state.show_detail = cid if cid in details else False
                if not st.session_state.show_detail:
                    st.session_state.show_back = False
                    st.session_state.card_index += 1
                st.rerun()
            if b2.button("曖昧", use_container_width=True):
                statuses[cid] = "fuzzy"; save_statuses(statuses)
                st.session_state.show_back = False
                st.session_state.show_detail = False
                st.session_state.card_index += 1
                st.rerun()
            if b3.button("わかった", use_container_width=True):
                statuses[cid] = "known"; save_statuses(statuses)
                st.session_state.show_back = False
                st.session_state.show_detail = False
                st.session_state.card_index += 1
                st.rerun()

        if st.session_state.show_detail and st.session_state.show_detail == cid:
            d = details[cid]
            st.markdown(f"""
            <div style="background:white;border:1px solid #b2e0dd;border-top:3px solid #0abab5;padding:28px 28px 24px;margin-top:8px;">
                <div style="font-family:'Cormorant Garamond',Georgia,serif;font-size:1.3rem;font-weight:400;color:#1a1a1a;letter-spacing:0.05em;margin-bottom:16px;">{d['title']}</div>
                {d['html']}
            </div>
            """, unsafe_allow_html=True)
            st.write("")
            if st.button("次のカードへ →", use_container_width=True, type="primary"):
                st.session_state.show_back = False
                st.session_state.show_detail = False
                st.session_state.card_index += 1
                st.rerun()

        st.write("")
        n1, n2 = st.columns(2)
        if n1.button("← 前へ", use_container_width=True, disabled=(idx == 0)):
            st.session_state.card_index = max(0, st.session_state.card_index - 1)
            st.session_state.show_back = False
            st.rerun()
        if n2.button("次へ →", use_container_width=True, disabled=(idx >= len(deck) - 1)):
            st.session_state.card_index += 1
            st.session_state.show_back = False
            st.rerun()

    st.write("")
    st.selectbox("カテゴリ", cats, key="study_cat")
    st.selectbox("習熟度", status_opts, key="study_status")

with tab2:
    query = st.text_input("用語を入力", placeholder="例：元利均等、擁壁、ROI…")
    if query:
        results = [c for c in all_cards if query in c["term"] or query in c.get("reading","") or query in c["meaning"]]
        if results:
            st.success(f"「{query}」の検索結果：{len(results)}件")
            for c in results:
                cid = str(c["id"])
                s = statuses.get(cid)
                icon = STATUS_ICONS.get(s, "—") if s else "—"
                with st.expander(f"{icon}  {c['term']}　{mapped_category(c)}"):
                    if c.get("reading"): st.caption(c["reading"])
                    st.write(c["meaning"])
                    if c.get("example"): st.info(c['example'])
        else:
            st.warning(f"「{query}」は単語帳にありません")
            if st.button("Claude に調べてもらう"):
                api_key = os.environ.get("ANTHROPIC_API_KEY", "")
                if not api_key:
                    st.error("ANTHROPIC_API_KEYが設定されていません。起動時に設定してください。")
                else:
                    with st.spinner(f"「{query}」を調べています…"):
                        try:
                            import anthropic
                            client = anthropic.Anthropic(api_key=api_key)
                            msg = client.messages.create(
                                model="claude-opus-4-5",
                                max_tokens=1024,
                                messages=[{"role": "user", "content": f'不動産・建築・土地活用営業の用語「{query}」について、以下のJSON形式のみで答えてください（前置き・コードブロック不要）：{{"term": "{query}", "reading": "よみがな", "category": "建築・法規か不動産・登記か営業・提案か社内・業界かビジネス用語", "meaning": "100字程度の説明", "example": "営業現場での使用例(なければ空)"}}'}]
                            )
                            text = msg.content[0].text
                            m = re.search(r'\{[\s\S]*\}', text)
                            if m:
                                st.session_state.ai_result = json.loads(m.group())
                        except Exception as e:
                            st.error(f"エラー: {e}")

            if st.session_state.ai_result:
                r = st.session_state.ai_result
                st.success("Claude が調べました")
                st.markdown(f"### {r.get('term', query)}")
                if r.get("reading"): st.caption(f"読み方：{r['reading']}")
                st.markdown(f"**カテゴリ：** {r.get('category','')}")
                st.write(r.get("meaning",""))
                if r.get("example"): st.info(r['example'])
                if st.button("＋ 単語帳に追加する", type="primary"):
                    new_card = {"id": f"custom_{len(custom_cards)+1}", "category": r.get("category","社内・業界"), "term": r.get("term", query), "reading": r.get("reading",""), "meaning": r.get("meaning",""), "example": r.get("example",""), "is_custom": True}
                    custom_cards.append(new_card)
                    save_custom(custom_cards)
                    st.session_state.ai_result = None
                    st.success("追加しました！")
                    st.rerun()

with tab3:
    cats_all = ["すべて"] + list(CATEGORY_COLORS.keys())
    list_cat = st.selectbox("カテゴリ", cats_all, key="list_cat")
    display = [c for c in all_cards if list_cat == "すべて" or mapped_category(c) == list_cat]
    st.caption(f"{len(display)}語")
    for c in display:
        cid = str(c["id"])
        s = statuses.get(cid)
        icon = STATUS_ICONS.get(s, "—") if s else "—"
        with st.expander(f"{icon}  {c['term']}"):
            if c.get("reading"): st.caption(c["reading"])
            st.write(c["meaning"])
            if c.get("example"): st.info(c['example'])

with tab4:
    st.subheader("新しい単語を追加")
    add_term = st.text_input("用語 *", placeholder="例：擁壁", key="add_term")
    add_reading = st.text_input("読み方", placeholder="例：ようへき", key="add_reading")
    cat_opts = list(CATEGORY_COLORS.keys())
    suggested = auto_category(add_term) if add_term else cat_opts[0]
    suggested_idx = cat_opts.index(suggested) if suggested in cat_opts else 0
    if add_term:
        st.caption(f"カテゴリ自動判定: {suggested}")
    add_category = st.selectbox("カテゴリ *", cat_opts, index=suggested_idx, key="add_category")
    add_meaning = st.text_area("意味・説明 *", placeholder="わかりやすく説明してみましょう", key="add_meaning")
    add_example = st.text_input("使用例（任意）", key="add_example")
    if st.button("追加する", type="primary", use_container_width=True, key="add_submit"):
        if not add_term or not add_meaning:
            st.error("用語と意味は必須です")
        else:
            new_card = {"id": f"custom_{len(custom_cards)+1}", "category": add_category, "term": add_term, "reading": add_reading, "meaning": add_meaning, "example": add_example, "is_custom": True}
            custom_cards.append(new_card)
            save_custom(custom_cards)
            st.success(f"「{add_term}」を追加しました！")
            st.rerun()

    if custom_cards:
        st.divider()
        st.subheader(f"追加済み（{len(custom_cards)}語）")
        for i, c in enumerate(custom_cards):
            ca, cb = st.columns([4, 1])
            ca.write(f"**{c['term']}** — {c['category']}")
            if cb.button("削除", key=f"del_{i}"):
                custom_cards.pop(i)
                save_custom(custom_cards)
                st.rerun()

st.divider()

col1, col2, col3, col4 = st.columns(4)
stat_box(col1, "わかった", known_n, "btn_known", "known")
stat_box(col2, "曖昧", fuzzy_n, "btn_fuzzy", "fuzzy")
stat_box(col3, "わからない", unknown_n, "btn_unknown", "unknown")
col4.markdown(f"""
<div style="background:#f0fafa;border:1px solid #b2e0dd;padding:18px 16px;text-align:center;">
  <div style="font-size:0.68rem;color:#888;letter-spacing:0.15em;" translate="no">合計</div>
  <div style="font-family:'Cormorant Garamond',serif;font-size:2rem;font-weight:400;color:#0abab5;">{rated}/{total}</div>
</div>""", unsafe_allow_html=True)

if total > 0:
    st.progress(known_n / total)

if st.session_state.status_filter:
    sf = st.session_state.status_filter
    label_map = {"known": "わかった", "fuzzy": "曖昧", "unknown": "わからない"}
    filtered = [c for c in all_cards if statuses.get(str(c["id"])) == sf]
    st.markdown(f"<div style='margin:16px 0 8px;font-size:0.8rem;color:#0abab5;letter-spacing:0.1em;'>— {label_map[sf]}　{len(filtered)}語 —</div>", unsafe_allow_html=True)
    for c in filtered:
        cid_f = str(c["id"])
        with st.expander(f"{c['term']}　{c.get('reading','')}"):
            st.write(c["meaning"])
            if c.get("example"): st.info(c["example"])
            if sf == "unknown":
                b1, b2, b3 = st.columns(3)
                if b1.button("未判定", key=f"to_none_{cid_f}", use_container_width=True):
                    statuses.pop(cid_f, None)
                    save_statuses(statuses)
                    st.rerun()
                if b2.button("曖昧", key=f"to_fuzzy_{cid_f}", use_container_width=True):
                    statuses[cid_f] = "fuzzy"
                    save_statuses(statuses)
                    st.rerun()
                if b3.button("わかった ✓", key=f"promote_{cid_f}", type="primary", use_container_width=True):
                    statuses[cid_f] = "known"
                    save_statuses(statuses)
                    st.rerun()
            elif sf == "fuzzy":
                b1, b2, b3 = st.columns(3)
                if b1.button("未判定", key=f"to_none_{cid_f}", use_container_width=True):
                    statuses.pop(cid_f, None)
                    save_statuses(statuses)
                    st.rerun()
                if b2.button("わからない", key=f"to_unknown_{cid_f}", use_container_width=True):
                    statuses[cid_f] = "unknown"
                    save_statuses(statuses)
                    st.rerun()
                if b3.button("わかった ✓", key=f"promote_{cid_f}", type="primary", use_container_width=True):
                    statuses[cid_f] = "known"
                    save_statuses(statuses)
                    st.rerun()
            elif sf == "known":
                b1, b2, b3 = st.columns(3)
                if b1.button("未判定", key=f"to_none_{cid_f}", use_container_width=True):
                    statuses.pop(cid_f, None)
                    save_statuses(statuses)
                    st.rerun()
                if b2.button("曖昧に戻す", key=f"to_fuzzy_{cid_f}", use_container_width=True):
                    statuses[cid_f] = "fuzzy"
                    save_statuses(statuses)
                    st.rerun()
                if b3.button("わからないに戻す", key=f"to_unknown_{cid_f}", use_container_width=True):
                    statuses[cid_f] = "unknown"
                    save_statuses(statuses)
                    st.rerun()
