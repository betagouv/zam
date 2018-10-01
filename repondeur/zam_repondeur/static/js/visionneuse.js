;(function toggleContent () {
  const toggleLinks = Array.from(document.querySelectorAll('[data-toggle-target]'))
  toggleLinks.forEach(toggleLink => {
    toggleLink.onclick = (e) => {
      const target = e.target
      const toggleTarget = document.querySelector(`#${target.dataset.toggleTarget}`)
      const toggleParent = toggleTarget.parentElement
      const removeArrows = () => {
        const arrowDownLink = document.querySelector('.arrow-down')
        if (arrowDownLink) {
          arrowDownLink.classList.remove('arrow', 'arrow-down')
          arrowDownLink.textContent = arrowDownLink.dataset.initialText
        }
      }
      const hideElement = () => {
        toggleParent.classList.replace('is-visible', 'is-hidden')
        removeArrows()
      }
      removeArrows()
      if (toggleParent.classList.contains('is-hidden')) {
        const visibleElement = document.querySelector('.is-visible')
        if (visibleElement) {
          visibleElement.classList.replace('is-visible', 'is-hidden')
        }
        toggleParent.classList.replace('is-hidden', 'is-visible')
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
;(function displayJumpToAmendementForm () {
  const link = document.querySelector('.find')
  const form = document.querySelector('#search-amendements')
  link.addEventListener('click', e => {
    e.preventDefault()
    form.classList.replace('is-hidden', 'is-visible')
    form.querySelector('#q').focus()
  })
})()
;(function jumpToAmendement () {
  const form = document.querySelector('#search-amendements')
  const input = form.querySelector('input[name="q"]')
  const matches = JSON.parse(form.dataset.amendementMatches)
  form.addEventListener('submit', e => {
    e.preventDefault()
    const form = e.target
    const data = new FormData(form)
    const value = data.get('q').trim()
    if (value in matches) {
      window.location = matches[value]
    } else {
      form.querySelector('.error').classList.remove('hide')
    }
  })
  input.addEventListener('keydown', e => {
    input.parentElement.querySelector('.error').classList.add('hide')
  })

})()
