'use strict';
const menu = document.getElementById('menu-button');
menu?.addEventListener('click', () => {
  const open = menu.getAttribute('aria-expanded') !== 'true';
  menu.setAttribute('aria-expanded', String(open));
  menu.textContent = open ? '目次をとじる' : '目次をひらく';
  document.getElementById('sidebar').classList.toggle('open', open);
});
function revealHash() {
  if (!location.hash) return;
  let id;
  try { id = decodeURIComponent(location.hash.slice(1)); } catch { return; }
  const target = document.getElementById(id);
  if (!target) return;
  let ancestor = target.parentElement;
  while (ancestor) {
    if (ancestor.tagName === 'DETAILS') ancestor.open = true;
    ancestor = ancestor.parentElement;
  }
  target.scrollIntoView({block: 'start'});
}
window.addEventListener('hashchange', revealHash);
document.addEventListener('click', (event) => {
  const link = event.target.closest('a[href^="#"]');
  if (link && link.hash === location.hash) revealHash();
});
revealHash();
window.addEventListener('beforeprint', () => {
  document.querySelectorAll('details:not([open])').forEach(el => { el.dataset.printOpened = '1'; el.open = true; });
});
window.addEventListener('afterprint', () => {
  document.querySelectorAll('[data-print-opened]').forEach(el => { el.open = false; delete el.dataset.printOpened; });
});

const form = document.getElementById('calc-form');
if (form) {
  const ids = ['people','records','api','photos','size','views','months'];
  const result = document.getElementById('calc-results');
  const fmt = (n, digits=2) => new Intl.NumberFormat('ja-JP', {maximumFractionDigits:digits}).format(n);
  function metric(label, value, ratio, detail) {
    const el = document.createElement('article');
    el.className = 'metric' + (ratio > 100 ? ' over' : '');
    const heading = document.createElement('h3'); heading.textContent = label;
    const number = document.createElement('strong'); number.textContent = value;
    const bar = document.createElement('progress'); bar.max = 100; bar.value = Math.min(ratio, 100);
    bar.setAttribute('aria-label', label + '：参考枠の' + fmt(ratio) + '%');
    const text = document.createElement('p'); text.textContent = (ratio > 100 ? '参考枠を超える目安。' : '') + detail;
    el.append(heading, number, bar, text); return el;
  }
  function calculate() {
    const fields = ids.map(id => document.getElementById(id));
    if (fields.some(el => !el.checkValidity() || !Number.isFinite(el.valueAsNumber))) {
      document.getElementById('calc-error').textContent = '入力できる範囲の数値を入れてね。人数は1人以上です。';
      result.replaceChildren(); return;
    }
    document.getElementById('calc-error').textContent = '';
    const [people, records, api, photos, size, views, months] = fields.map(el => el.valueAsNumber);
    const db = people * records * 365 * 2 / 1000 * 3;
    const requests = people * api;
    const docs = requests * 20;
    const text = docs * 2 * 30 / 1000000;
    const imageMonth = people * photos * size * 30 / 1000;
    const storage = imageMonth * months;
    const transfer = text + imageMonth * views;
    result.replaceChildren(
      metric('DBの年間増分（仮定）', fmt(db) + ' MB / 年', db / 500 * 100, '参考500 MBの' + fmt(db/5) + '%。既存DB・認証等を含まないよ。'),
      metric('データ取得API', fmt(requests,0) + ' 回 / 日', requests / 100000 * 100, 'Workers 10万回/日と比較。書込・ログイン・CPUは別。'),
      metric('返す行・文書の数', fmt(docs,0) + ' 件 / 日', docs / 50000 * 100, 'Firestore 5万読取/日の参考値。D1の走査行数ではないよ。'),
      metric('テキストの転送量', fmt(text) + ' GB / 月', text / 5 * 100, 'Supabase非キャッシュ5 GB/月と比較。画像・アプリ本体は別。'),
      metric('写真の保存量', fmt(storage) + ' GB', storage * 100, '参考1 GBと比較。毎月' + fmt(imageMonth) + ' GB増え、' + fmt(months,0) + 'か月保持する仮定。'),
      metric('テキスト＋写真の転送', fmt(transfer) + ' GB / 月', transfer / 5 * 100, '全件非キャッシュの仮定。過去の写真の追加配信を含まないよ。')
    );
  }
  form.addEventListener('input', calculate);
  form.addEventListener('submit', event => event.preventDefault());
  document.querySelectorAll('[data-preset]').forEach(button => button.addEventListener('click', () => {
    form.reset();
    const preset = button.dataset.preset;
    if (preset === '50') document.getElementById('people').value = 50;
    if (preset === 'text') document.getElementById('photos').value = 0;
    calculate();
  }));
  calculate();
}

const authWalkthrough = document.querySelector('[data-auth-walkthrough]');
if (authWalkthrough) {
  const controls = authWalkthrough.querySelector('.auth-step-controls');
  const buttons = Array.from(controls.querySelectorAll('[data-auth-step]'));
  const scenes = Array.from(authWalkthrough.querySelectorAll('[data-auth-scene]'));
  const map = authWalkthrough.querySelector('.auth-map');
  const announcement = authWalkthrough.querySelector('.auth-scene-announcement');
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  function showAuthScene(key, announce) {
    const scene = scenes.find(item => item.dataset.authScene === key);
    if (!scene) return;
    buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.authStep === key)));
    scenes.forEach(item => { item.hidden = item !== scene; });
    map.querySelectorAll('[data-auth-value]').forEach(label => {
      label.textContent = scene.getAttribute('data-' + label.dataset.authValue);
    });
    map.querySelectorAll('[data-auth-route]').forEach(route => {
      const direction = scene.getAttribute('data-' + route.dataset.authRoute);
      route.dataset.direction = direction || '';
      const signal = route.querySelector('.auth-map-signal');
      signal.getAnimations?.().forEach(animation => animation.cancel());
      if (direction && announce && !reducedMotion.matches) {
        signal.animate?.([{strokeDashoffset: 1}, {strokeDashoffset: 0}], {duration: 420, easing: 'ease-out'});
      }
    });
    if (announce) announcement.textContent = scene.innerText.trim();
  }

  controls.addEventListener('click', event => {
    const button = event.target.closest('button[data-auth-step]');
    if (button?.getAttribute('aria-pressed') === 'false') showAuthScene(button.dataset.authStep, true);
  });
  showAuthScene(buttons[0].dataset.authStep, false);
  controls.hidden = false;
  map.hidden = false;
}
