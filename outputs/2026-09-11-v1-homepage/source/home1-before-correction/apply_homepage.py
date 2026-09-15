from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlencode
import json

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
target = ROOT / 'v1/html/index.html'
soup = BeautifulSoup((OUT / 'source/before-index.html').read_text(), 'html.parser')
hero = soup.select_one('.hero.hero-photo')
original = hero.select_one('.container')
for element in original.select('.reveal'):
    element['class'] = [c for c in element['class'] if c != 'reveal']

fragment = BeautifulSoup('''
<section class="hero hero-photo home-carousel" id="home-banner" data-home-carousel role="region" aria-roledescription="輪播" aria-label="TIRI 首頁焦點">
  <div class="home-slide is-active" id="home-slide-1" role="group" aria-roledescription="投影片" aria-label="第 1 張，共 3 張：TIRI 首頁" aria-hidden="false" data-slide-name="TIRI 首頁" style="--slide-image:url('../images/event-2025-conference-official.jpg')">
    <img class="home-slide__image" src="../images/event-2025-conference-official.jpg" alt="TIRI 2025 年度大會合影" width="2400" height="1600" fetchpriority="high" decoding="async">
  </div>
  <div class="home-slide" id="home-slide-2" role="group" aria-roledescription="投影片" aria-label="第 2 張，共 3 張：董監事進修課程" aria-hidden="true" inert data-slide-name="董監事進修課程" style="--slide-image:url('../images/review-r5/board-training-collage-nine.png')">
    <img class="home-slide__image" src="../images/review-r5/board-training-collage-nine.png" alt="九張董監事進修與協會活動照片拼接" width="1774" height="887" decoding="async">
    <div class="container"><div class="hero-grid"><div><p class="eyebrow">Courses &amp; Continuing Education</p><h2><span class="seg">董監事</span><br><span class="seg">進修課程</span></h2></div><div class="hero-side"><p>可申報上市上櫃公司董事、公司治理主管年度進修時數。</p><div class="hero-cta"><a class="btn btn-primary" href="trainbod.html">了解進修課程 <span aria-hidden="true" class="arrow">→</span></a><a class="arrow-link u-link" href="trainbod.html#inhouse">八大課程主題</a></div></div></div></div>
  </div>
  <div class="home-slide" id="home-slide-3" role="group" aria-roledescription="投影片" aria-label="第 3 張，共 3 張：董事會績效評估" aria-hidden="true" inert data-slide-name="董事會績效評估" style="--slide-image:url('../images/review-r2/business-team.jpg')">
    <img class="home-slide__image" src="../images/review-r2/business-team.jpg" alt="企業團隊討論與文件審閱情境" width="1920" height="1280" decoding="async">
    <div class="container"><div class="hero-grid"><div><p class="eyebrow">Board Performance Evaluation</p><h2><span class="seg">董事會</span><br><span class="seg">績效評估</span></h2></div><div class="hero-side"><p>以務實且高效方式，協助企業落實公司治理、促進董事會管理效能。</p><div class="hero-cta"><a class="btn btn-primary" href="bodperform.html">了解評估服務 <span aria-hidden="true" class="arrow">→</span></a><a class="arrow-link u-link" href="bodperform.html#process">查看評估流程</a></div></div></div></div>
  </div>
  <div class="home-carousel__controls container" hidden><div class="home-carousel__bar">
    <div class="home-carousel__selectors" role="group" aria-label="選擇 Banner">
      <button type="button" class="home-carousel__selector" data-slide-to="0" aria-controls="home-slide-1" aria-current="true" aria-label="顯示第 1 張：TIRI 首頁"><span>01</span> TIRI 首頁</button>
      <button type="button" class="home-carousel__selector" data-slide-to="1" aria-controls="home-slide-2" aria-current="false" aria-label="顯示第 2 張：董監事進修課程"><span>02</span> 董監事課程</button>
      <button type="button" class="home-carousel__selector" data-slide-to="2" aria-controls="home-slide-3" aria-current="false" aria-label="顯示第 3 張：董事會績效評估"><span>03</span> 績效評估</button>
    </div>
    <div class="home-carousel__navigation"><span class="home-carousel__count" data-carousel-count aria-hidden="true">01 / 03</span><button type="button" class="home-carousel__toggle" data-carousel-toggle aria-label="暫停輪播">暫停輪播</button><button type="button" class="home-carousel__arrow" data-carousel-prev aria-label="上一張 Banner">←</button><button type="button" class="home-carousel__arrow" data-carousel-next aria-label="下一張 Banner">→</button></div>
  </div></div>
  <p class="home-carousel__status" data-carousel-status role="status" aria-atomic="true"></p>
</section>''', 'html.parser')
fragment.select_one('#home-slide-1').append(original.extract())
hero.replace_with(fragment.section)

address = '台北市中正區重慶南路一段57號'
map_src = json.loads((OUT / 'source/Google地圖嵌入.json').read_text())['embedUrl']
map_link = 'https://www.google.com/maps/search/?' + urlencode({'api': 1, 'query': address})
contact = BeautifulSoup('''
<section class="home-section home-contact" id="contact" aria-labelledby="home-contact-heading"><div class="container home-contact__grid">
  <div><p class="eyebrow">Contact TIRI</p><h2 id="home-contact-heading">聯絡我們</h2>
    <dl class="home-contact__details"><div><dt>電話</dt><dd><a class="u-link" href="tel:+886223819248">(02) 2381-9248</a></dd></div><div><dt>電子信箱</dt><dd><a class="u-link" href="mailto:office@tiri.tw">office@tiri.tw</a></dd></div><div><dt>地址</dt><dd>台北市中正區重慶南路一段 57 號<br>13 樓之 13</dd></div></dl>
    <p class="home-contact__access">台新銀行樓上<br>捷運台大醫院站 4 號出口，步行約三分鐘。</p>
    <a class="u-link arrow-link" href="contact.html">更多聯絡資訊與留言</a>
  </div>
  <div class="home-contact__map"><div class="map-frame"><iframe title="TIRI 聯絡地址 Google 地圖：台北市中正區重慶南路一段 57 號" width="720" height="400" loading="lazy" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div><p><a class="u-link" target="_blank" rel="noopener" data-map-link>開啟 Google 地圖 ↗</a></p></div>
</div></section>''', 'html.parser')
contact.iframe['src'] = map_src
contact.select_one('[data-map-link]')['href'] = map_link
soup.select_one('main').append(contact.section)
soup.head.append(soup.new_tag('link', attrs={'rel': 'stylesheet', 'href': '../css/homepage.css?v=20260911-home1'}))
soup.body.append(soup.new_tag('script', attrs={'defer': '', 'src': '../js/homepage.js?v=20260911-home1'}))
target.write_text(str(soup))
print('Homepage: three-slide carousel and contact map applied.')
