/* Shared rendering for the editor and the printed certificate. */
window.CertificatePage = {
  fit(page) {
    page.querySelectorAll('.certificate-text').forEach(text => {
      const box = text.parentElement;
      let size = Number(box.dataset.size);
      text.style.fontSize = `${size}pt`;
      while ((text.scrollHeight > box.clientHeight + 1 || text.scrollWidth > box.clientWidth + 1) && size > 6) {
        size -= .5;
        text.style.fontSize = `${size}pt`;
      }
    });
  },
  render(page, elements) {
    page.replaceChildren();
    elements.forEach(item => {
      const box = document.createElement('div');
      box.className = 'certificate-element';
      box.dataset.id = item.id;
      box.dataset.size = item.size;
      Object.assign(box.style, {
        left: `${item.x}mm`, top: `${item.y}mm`, width: `${item.w}mm`, height: `${item.h}mm`,
        fontSize: `${item.size}pt`, fontWeight: item.bold ? '700' : '400', textAlign: item.align,
        color: item.color, fontFamily: item.font || 'Sarabun', opacity: item.opacity, zIndex: item.z, display: item.visible ? 'block' : 'none'
      });
      if (item.kind === 'image') {
        if (item.value) { const img = document.createElement('img'); img.src = item.value; img.alt = ''; box.append(img); }
      } else if (item.kind === 'line') {
        box.style.borderTop = `1px solid ${item.color}`;
      } else {
        const text = document.createElement('span'); text.className = 'certificate-text';
        text.textContent = item.kind === 'text' && item.text !== undefined ? item.text : item.value;
        box.append(text);
      }
      page.append(box);
    });
    this.fit(page);
    document.fonts.ready.then(() => this.fit(page));
  }
};
