application.register(
  'table-anchor',
  class extends Stimulus.Controller {
    initialize() {
      if (location.hash) {
        /* Waiting for the next tick to supplement previous browser behavior. */
        setTimeout(() => {
          const element = document.querySelector(window.location.hash)
          const target = element.getBoundingClientRect()
          window.scrollTo({
            /* Position the highlighted element in the middle of the page. */
            top:
              window.scrollY +
              target.top -
              window.innerHeight / 2 +
              target.height / 2,
            behavior: 'smooth'
          })
        }, 1)
      }
    }
  }
)

class TableFilters extends Stimulus.Controller {
  static get targets() {
    return [
      'row',
      'link',
      'bottom',
      'count',
      'table',
      'tbody',
      'articleInput',
      'amendementInput',
      'gouvernementalCheckbox',
      'gouvernementalLabel'
    ]
  }

  initialize() {
    const articleFilter = this.getURLParam('article')
    if (articleFilter !== '') {
      this.toggle()
      this.articleInputTarget.value = articleFilter
      this.filterByArticle(articleFilter)
    }
    const amendementFilter = this.getURLParam('amendement')
    if (amendementFilter !== '') {
      this.toggle()
      this.amendementInputTarget.value = amendementFilter
      this.filterByAmendement(amendementFilter)
    }
    const gouvernementalFilter = this.getURLParam('gouvernemental')
    if (gouvernementalFilter !== '') {
      this.toggle()
      this.gouvernementalCheckboxTarget.checked = true
      this.gouvernementalLabelTarget
        .querySelector('abbr')
        .classList.add('selected')
      this.filterByGouvernemental(gouvernementalFilter)
    }
    this.updateCount()
  }

  getURLParam(name) {
    const urlParams = new URLSearchParams(window.location.search)
    return urlParams.get(name) || ''
  }

  setURLParam(name, value) {
    if (history.replaceState) {
      const newURL = new URL(window.location.href)
      if (value !== '') {
        newURL.searchParams.set(name, value)
      } else {
        newURL.searchParams.delete(name)
      }
      window.history.replaceState({ path: newURL.href }, '', newURL.href)
    }
  }

  toggle(event) {
    if (this.hasLinkTarget && this.hasRowTarget) {
      this.linkTarget.classList.toggle('enabled')
      this.rowTarget.classList.toggle('d-none')
      this.bottomTarget.classList.toggle('d-none')
    }
    if (event) event.preventDefault()
  }

  updateCount() {
    const initial = parseInt(this.data.get('initial-count'))
    const visibleRows = this.tbodyTarget.querySelectorAll(
      'tr:not([class^=hidden]):not([class=limit-derouleur])'
    )
    if (!visibleRows.length) {
      this.countTarget.innerHTML = `Aucun amendement (${initial.toLocaleString('fr')} au total)`
      return
    }
    const current = Array.from(visibleRows).reduce(
      (accumulator, currentValue) => {
        return accumulator + currentValue.dataset.amendement.split(',').length
      },
      0
    )
    const plural = current > 1 ? 's' : ''
    if (initial === current)
      this.countTarget.innerHTML = `${current.toLocaleString('fr')} amendement${plural}`
    else
      this.countTarget.innerHTML = `${current.toLocaleString('fr')} amendement${plural} (${initial.toLocaleString('fr')} au total)`
  }

  filterArticle(event) {
    const value = event.target.value.trim()
    this.filterByArticle(value)
    this.setURLParam('article', value)
    this.updateCount()
  }

  filterAmendement(event) {
    const value = event.target.value.trim()
    this.filterByAmendement(value)
    this.setURLParam('amendement', value)
    this.updateCount()
  }

  filterGouvernemental(event) {
    const checked = event.target.checked
    const value = checked ? '1' : ''
    this.gouvernementalLabelTarget
      .querySelector('abbr')
      .classList.toggle('selected', checked)
    this.filterByGouvernemental(value)
    this.setURLParam('gouvernemental', value)
    this.updateCount()
  }

  filterByArticle(value) {
    this.filterColumn('hidden-article', line => {
      if (!value) {
        return true
      }
      if (value.includes(' ')) {
        // Special case of `6 b` for `6 bis` for instance.
        return line.dataset.article.startsWith(value)
      } else {
        return line.dataset.article.trim() === value
      }
    })
  }

  filterByAmendement(value) {
    this.filterColumn('hidden-amendement', line => {
      if (!value) {
        return true
      }
      return line.dataset.amendement
        .split(',')
        .some(num => num.toLowerCase().startsWith(value.toLowerCase()))
    })
    this.tableTarget.classList.toggle('filtered-amendement', value)
  }

  filterByGouvernemental(value) {
    this.filterColumn('hidden-gouvernemental', line => {
      if (!value) {
        return true
      }
      return line.dataset.gouvernemental.trim() === value
    })
    this.tableTarget.classList.toggle('filtered-gouvernemental', value)
  }

  filterColumn(className, shouldShow) {
    this.tbodyTarget.querySelectorAll('tr').forEach(line => {
      line.classList.toggle(className, !shouldShow(line))
    })
  }
}

application.register(
  'table-selection',
  class extends Stimulus.Controller {
    static get targets() {
      return ['filters', 'bottom']
    }
    initialize() {
      this.groupActions = this.element.querySelector('.groupActions')
      this.batchAmendementsLink = this.groupActions.querySelector(
        '#batch-amendements'
      )
      this.selectAllCheckbox = this.element.querySelector(
        'thead input[type="checkbox"][name="select-all"]'
      )
      // Useful in case of (soft) refresh with already checked box.
      this.selectAllCheckbox.checked = false
      this.checkboxes = this.element.querySelectorAll(
        'tbody input[type="checkbox"]:not([name="select-all"])'
      )
      // Useful in case of (soft) refresh with already checked boxes.
      this.toggleGroupActions()
      this.checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', e => {
          this.toggleGroupActions()
        })
      })
    }

    fromSameArticle(checkeds) {
      const articleNumFromChecked = item =>
        item.closest('tr').dataset.article.trim()
      const firstArticleChecked = articleNumFromChecked(checkeds[0])
      return checkeds.every(
        checked => articleNumFromChecked(checked) === firstArticleChecked
      )
    }

    fromSameMission(checkeds) {
      const missionFromChecked = item => item.closest('tr').dataset.mission
      const firstMissionChecked = missionFromChecked(checkeds[0])
      return checkeds.every(
        checked => missionFromChecked(checked) === firstMissionChecked
      )
    }

    toggleGroupActions() {
      const checkeds = Array.from(this.checkboxes).filter(box => box.checked)
      const checkedsLength = checkeds.length
      this.groupActions.classList.toggle('d-none', checkeds.length < 1)
      if (this.batchAmendementsLink) {
        this.batchAmendementsLink.classList.toggle('d-none', checkedsLength < 2)
        if (checkedsLength >= 2) {
          this.batchAmendementsLink.classList.toggle(
            'd-none',
            !(this.fromSameArticle(checkeds) && this.fromSameMission(checkeds))
          )
        }
      }
      if (checkedsLength < 1) {
        this.filtersTarget
          .querySelectorAll('th')
          .forEach(th => (th.style.top = '0'))
        this.bottomTarget
          .querySelectorAll('th')
          .forEach(th => (th.style.top = '3rem'))
      } else {
        this.filtersTarget
          .querySelectorAll('th')
          .forEach(th => (th.style.top = '3.8rem'))
        this.bottomTarget
          .querySelectorAll('th')
          .forEach(th => (th.style.top = '7rem'))
      }
      this.changeURLGivenChecks(
        this.groupActions.querySelector('#transfer-amendements'),
        checkeds
      )
      if (checkedsLength >= 2 && this.batchAmendementsLink) {
        this.changeURLGivenChecks(this.batchAmendementsLink, checkeds)
      }
    }

    changeURLGivenChecks(target, checkeds) {
      const url = new URL(target.getAttribute('href'))
      url.searchParams.delete('n')
      checkeds.forEach(checked => {
        url.searchParams.append('n', checked.value)
      })
      target.setAttribute('href', url.toString())
    }

    selectAll() {
      this.checkboxes.forEach(checkbox => {
        if (checkbox.offsetParent !== null) {
          checkbox.checked = this.selectAllCheckbox.checked
        }
      })
      this.toggleGroupActions()
    }
  }
)
