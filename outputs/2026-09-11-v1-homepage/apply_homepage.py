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
fragment = BeautifulSoup('''
<section class="hero hero-photo home-carousel" id="home-banner" data-home-carousel>
  <div class="home-carousel__images" aria-hidden="true">
    <div class="home-slide is-active" style="--slide-image:url('../images/event-2025-conference-official.jpg')">
      <img class="home-slide__image" src="../images/event-2025-conference-official.jpg" alt="" width="2400" height="1600" fetchpriority="high" decoding="async">
    </div>
    <div class="home-slide" style="--slide-image:url('../images/review-r5/board-training-collage-nine.png')">
      <img class="home-slide__image" src="../images/review-r5/board-training-collage-nine.png" alt="" width="1774" height="887" decoding="async">
    </div>
    <div class="home-slide" style="--slide-image:url('../images/review-r2/business-team.jpg')">
      <img class="home-slide__image" src="../images/review-r2/business-team.jpg" alt="" width="1920" height="1280" decoding="async">
    </div>
  </div>
</section>''', 'html.parser')
fragment.section.append(original.extract())
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
soup.head.append(soup.new_tag('link', attrs={'rel': 'stylesheet', 'href': '../css/homepage.css?v=20260911-home2'}))
soup.body.append(soup.new_tag('script', attrs={'defer': '', 'src': '../js/homepage.js?v=20260911-home2'}))
target.write_text(str(soup))
print('Homepage: three background images with fixed original text and contact map applied.')
