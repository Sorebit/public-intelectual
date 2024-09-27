function extractLinks(cls) {
  const elems = document.querySelectorAll(`a.${cls}`)
  const result = new Array()
  for (let i = 0; i < elems.length; i++) {
    const href = elems[i].attributes['href'].value
    if (href.startsWith('/film/')) {
      result.push(href)
    }
  }
  console.log(result.length)
  return result
}

function downloadText(filename, text) {
  const element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
  element.setAttribute('download', filename);
  document.body.appendChild(element);
  element.click();
  document.body.removeChild(element);
}

function download(cls, filename) {
  filename = filename || 'links.txt'
  const links = extractLinks(cls)
  downloadText(filename, links.join('\n') + '\n')
}
