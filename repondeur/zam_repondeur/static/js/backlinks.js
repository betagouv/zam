application.register(
  'backlinks',
  class extends Stimulus.Controller {
    update(event) {
      event.preventDefault()
      const thisURL = new URL(window.location.href)
      const linkURL = new URL(event.target.href)
      thisURL.hash = ''
      linkURL.searchParams.set('back', thisURL.pathname + thisURL.search)
      const href = linkURL.toString()
      if (
        event.ctrlKey ||
        event.shiftKey ||
        event.metaKey || // apple
        (event.button && event.button == 1) // middle click, >IE9 + everyone else
      ) {
        window.open(href).focus()
      } else {
        window.location.href = href
      }
    }
  }
)
