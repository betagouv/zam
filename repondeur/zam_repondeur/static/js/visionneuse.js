;(function toggleContent () {
  const toggleLinks = Array.from(document.querySelectorAll('[data-toggle-target]'))
  toggleLinks.forEach(toggleLink => {
    toggleLink.onclick = (e) => {
      e.preventDefault()
      const target = e.target
      const toggleTarget = document.querySelector(`#${target.dataset.toggleTarget}`)
      const toggleParent = toggleTarget.parentElement
      const superParent = target.parentElement.parentElement.parentElement
      const fakeAnchor = superParent.querySelector('.fake-anchor')
      if (fakeAnchor) {
        fakeAnchor.scrollIntoView({behavior: "smooth"})
      } else /* In case of article text. */ {
        window.scrollTo({
          top: 0,
          behavior: "smooth"
        })
      }
      const removeArrows = () => {
        const arrowDownLink = document.querySelector('.arrow-down')
        if (arrowDownLink) {
          arrowDownLink.classList.remove('arrow', 'arrow-down')
          arrowDownLink.textContent = arrowDownLink.dataset.initialText
        }
      }
      const hideElement = () => {
        toggleParent.classList.replace('is-block', 'is-none')
        removeArrows()
      }
      removeArrows()
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
;(function toggleAmendementSearchForm () {
  const link = document.querySelector('.find')
  const form = document.querySelector('#search-amendements')
  link.addEventListener('click', e => {
    e.preventDefault()
    if (form.classList.contains('is-none')) {
      form.classList.replace('is-none', 'is-flex')
      form.querySelector('#q-amendement').focus()
      window.scrollTo({
        top: 0,
        behavior: "smooth"
      })
    } else {
      form.classList.replace('is-flex', 'is-none')
    }
  })
})()
;(function jumpToAmendement () {
  const form = document.querySelector('#search-amendements')
  const input = form.querySelector('input[name="q-amendement"]')
  const matches = JSON.parse(form.dataset.amendementMatches)
  form.addEventListener('submit', e => {
    e.preventDefault()
    const form = e.target
    const data = new FormData(form)
    const value = data.get('q-amendement').trim()
    if (value in matches) {
      window.location = matches[value]
    } else {
      form.querySelector('.error').classList.remove('hide')
    }
  })
  input.addEventListener('keydown', e => {
    form.querySelector('.error').classList.add('hide')
  })

})()
