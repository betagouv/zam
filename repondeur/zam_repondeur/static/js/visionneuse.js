;(function toggleContent() {
  const toggleLinks = Array.from(
    document.querySelectorAll('[data-toggle-target]')
  )
  toggleLinks.forEach(toggleLink => {
    toggleLink.onclick = e => {
      e.preventDefault()
      const target = e.target
      const toggleTarget = document.querySelector(
        `#${target.dataset.toggleTarget}`
      )
      const toggleParent = toggleTarget.parentElement
      const superParent = target.parentElement.parentElement.parentElement
      const removeArrows = () => {
        const arrowDownLink = document.querySelector('.arrow-down')
        if (arrowDownLink) {
          arrowDownLink.classList.remove('arrow', 'arrow-down')
          arrowDownLink.textContent = arrowDownLink.dataset.initialText
        }
      }
      removeArrows()
      /* Wait for content to be actually removed through removeArrows
         otherwise scrollIntoView will fail to do the maths correctly.
         TODO: use Promises? */
      setTimeout(() => {
        const fakeAnchor = superParent.querySelector('.fake-anchor')
        if (fakeAnchor) {
          fakeAnchor.scrollIntoView({ behavior: 'smooth' })
        } /* In case of article text. */ else {
          window.scrollTo({
            top: 0,
            behavior: 'smooth'
          })
        }
      }, 1)
      const hideElement = () => {
        toggleParent.classList.replace('is-block', 'is-none')
        removeArrows()
      }
      if (toggleParent.classList.contains('is-none')) {
        const visibleElement = document.querySelector('.is-block')
        if (visibleElement) {
          visibleElement.classList.replace('is-block', 'is-none')
        }
        toggleParent.classList.replace('is-none', 'is-block')
        toggleParent.querySelector('.bottom a').onclick = hideElement
        target.dataset.initialText = target.textContent
        target.textContent = 'Replier'
        target.classList.add('arrow', 'arrow-down')
      } else {
        hideElement()
      }
    }
  })
})()
;(function toggleAmendementSearchForm() {
  const link = document.querySelector('.find')
  const form = document.querySelector('#search-amendements')
  link.addEventListener('click', e => {
    e.preventDefault()
    if (form.classList.contains('is-none')) {
      form.classList.replace('is-none', 'is-flex')
      form.querySelector('#q-amendement').focus()
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      })
    } else {
      form.classList.replace('is-flex', 'is-none')
    }
  })
})()
;(function jumpToAmendement() {
  const form = document.querySelector('#search-amendements')
  const input = form.querySelector('input[name="q-amendement"]')
  const urlSearchAmendement = form.dataset.urlSearchAmendement
  const error = form.querySelector('.error')
  form.addEventListener('submit', e => {
    e.preventDefault()
    const form = e.target
    const data = new FormData(form)
    const value = data.get('q-amendement').trim()
    const url = new URL(urlSearchAmendement)
    url.search = `num=${value}`
    fetch(url)
      .then(response => response.json())
      .then(urls => {
        if ('visionneuse' in urls) {
          window.location = urls['visionneuse']
        } else {
          error.classList.remove('hide')
        }
      })
      .catch(e => error.classList.remove('hide'))
  })
  input.addEventListener('keydown', e => error.classList.add('hide'))
})()
