(() => {
  const page = document.getElementById('certificate-page');
  const select = document.getElementById('element-select');
  const status = document.getElementById('save-status');
  const controls = [...document.querySelectorAll('[data-prop]')];
  let elements = JSON.parse(document.getElementById('certificate-elements').textContent);
  let selected = elements[0].id, dirty = false, revision = 0;
  const current = () => elements.find(item => item.id === selected);
  const changed = () => { dirty = true; revision++; status.textContent = 'มีการแก้ไขที่ยังไม่ได้บันทึก'; status.dataset.state = 'dirty'; };
  const constrain = item => {
    item.w = Math.max(1, Math.min(297, item.w)); item.h = Math.max(1, Math.min(210, item.h));
    item.x = Math.round(Math.max(0, Math.min(297 - item.w, item.x)) * 10) / 10;
    item.y = Math.round(Math.max(0, Math.min(210 - item.h, item.y)) * 10) / 10;
  };
  elements.forEach(item => { const option = document.createElement('option'); option.value = item.id; option.textContent = item.label; select.append(option); });
  function draw() {
    CertificatePage.render(page, elements);
    const box = [...page.children].find(node => node.dataset.id === selected);
    if (box) {
      box.classList.add('selected');
      if (!current().locked) { const handle = document.createElement('span'); handle.className = 'resize-handle'; box.append(handle); }
    }
    ['vertical', 'horizontal'].forEach(direction => { const guide = document.createElement('div'); guide.className = `guide ${direction}`; page.append(guide); });
    select.value = selected;
    controls.forEach(input => {
      const prop = input.dataset.prop;
      if (input.type === 'checkbox') input.checked = current()[prop];
      else input.value = prop === 'text' ? (current().text ?? current().value) : current()[prop];
    });
    document.getElementById('text-label').hidden = current().kind !== 'text';
    document.getElementById('typography-properties').hidden = !['text', 'dynamic'].includes(current().kind);
    document.getElementById('color-label').hidden = current().kind === 'image';
    document.getElementById('element-kind').textContent = {text:'ข้อความ', dynamic:'ข้อมูลอัตโนมัติ', image:'รูปภาพ', line:'เส้นคั่น'}[current().kind];
  }
  function zoom() {
    const workspace = document.querySelector('.designer-workspace');
    const value = document.getElementById('zoom').value;
    const style = getComputedStyle(workspace);
    const available = workspace.clientWidth - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight);
    const scale = value === 'fit' ? Math.max(.1, Math.min(1, available / page.offsetWidth)) : Number(value);
    page.style.transform = `scale(${scale})`;
    page.parentElement.style.width = `${page.offsetWidth * scale}px`;
    page.parentElement.style.height = `${page.offsetHeight * scale}px`;
  }
  select.addEventListener('change', () => { selected = select.value; draw(); });
  controls.forEach(input => input.addEventListener('change', () => {
    if (!input.checkValidity()) { input.reportValidity(); draw(); return; }
    current()[input.dataset.prop] = input.type === 'checkbox' ? input.checked : input.type === 'number' ? Number(input.value) : input.value;
    constrain(current()); changed(); draw();
  }));
  let drag = null;
  page.addEventListener('pointerdown', event => {
    if (event.button !== 0) return;
    const box = event.target.closest('.certificate-element');
    if (!box) return;
    const resizing = event.target.classList.contains('resize-handle');
    selected = box.dataset.id;
    const item = current();
    if (!item.locked) {
      const rect = page.getBoundingClientRect();
      drag = { id: event.pointerId, clientX:event.clientX, clientY:event.clientY, x:item.x, y:item.y, w:item.w, h:item.h, resizing, ratio:297 / rect.width };
      page.setPointerCapture(event.pointerId);
    }
    draw(); event.preventDefault();
  });
  page.addEventListener('pointermove', event => {
    if (!drag || event.pointerId !== drag.id) return;
    const item = current(), dx = (event.clientX - drag.clientX) * drag.ratio, dy = (event.clientY - drag.clientY) * drag.ratio;
    if (drag.resizing) {
      item.w = Math.round(Math.max(1, Math.min(297 - item.x, drag.w + dx)) * 10) / 10;
      item.h = Math.round(Math.max(1, Math.min(210 - item.y, drag.h + dy)) * 10) / 10;
    } else {
      item.x = drag.x + dx; item.y = drag.y + dy;
      if (Math.abs(item.x + item.w / 2 - 148.5) < 2) item.x = 148.5 - item.w / 2;
      if (Math.abs(item.y + item.h / 2 - 105) < 2) item.y = 105 - item.h / 2;
    }
    constrain(item); changed(); draw();
  });
  ['pointerup', 'pointercancel', 'lostpointercapture'].forEach(type => page.addEventListener(type, () => { drag = null; }));
  document.getElementById('zoom').addEventListener('change', zoom);
  document.getElementById('reset-layout').addEventListener('click', () => {
    if (!window.confirm('คืนตำแหน่งและข้อความเริ่มต้น? ต้องกดบันทึกเพื่อใช้งานจริง')) return;
    elements = JSON.parse(document.getElementById('certificate-defaults').textContent); changed(); draw();
  });
  document.getElementById('preview-print').addEventListener('click', async () => {
    await document.fonts.ready; CertificatePage.fit(page); window.print();
  });
  window.addEventListener('beforeprint', () => {
    document.getElementById('certificate-print-copy')?.remove();
    const copy = page.cloneNode(true);
    copy.id = 'certificate-print-copy';
    copy.querySelectorAll('.guide,.resize-handle').forEach(node => node.remove());
    document.body.append(copy);
  });
  window.addEventListener('afterprint', () => document.getElementById('certificate-print-copy')?.remove());
  document.getElementById('save-layout').addEventListener('click', async event => {
    const button = event.currentTarget, savedRevision = revision;
    const props = ['x','y','w','h','size','font','bold','color','align','opacity','z','visible','locked'];
    const layout = Object.fromEntries(elements.map(item => [item.id, Object.fromEntries(
      [...props, ...(item.kind === 'text' ? ['text'] : [])].map(prop => [prop, prop === 'text' ? (item.text ?? item.value) : item[prop]])
    )]));
    button.disabled = true; status.textContent = 'กำลังบันทึก…'; status.dataset.state = 'saving';
    try {
      const response = await fetch(location.pathname, {method:'POST', headers:{'Content-Type':'application/json','X-CSRFToken':document.querySelector('[name=csrfmiddlewaretoken]').value}, body:JSON.stringify(layout)});
      if (!response.ok) { let message = 'บันทึกไม่สำเร็จ กรุณาตรวจสิทธิ์หรือเข้าสู่ระบบใหม่'; try { message = (await response.json()).error || message; } catch (_) {} throw new Error(message); }
      if (response.redirected) throw new Error('กรุณาเข้าสู่ระบบใหม่ก่อนบันทึก');
      dirty = revision !== savedRevision; status.textContent = dirty ? 'บันทึกแล้ว แต่มีการแก้ไขใหม่ที่ยังไม่ได้บันทึก' : 'บันทึกแล้ว — หน้าพิมพ์ใช้แม่แบบนี้แล้ว';
      status.dataset.state = dirty ? 'dirty' : 'saved';
    } catch (error) { status.textContent = error.message; status.dataset.state = 'error'; }
    finally { button.disabled = false; }
  });
  window.addEventListener('beforeunload', event => { if (dirty) { event.preventDefault(); event.returnValue = ''; } });
  draw(); zoom();
  new ResizeObserver(zoom).observe(document.querySelector('.studio-canvas'));
})();
