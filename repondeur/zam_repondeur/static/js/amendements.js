application.register(
  'amendements-backlinks',
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

application.register(
  'amendements-selection',
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
      const missionFromChecked = item =>
        item.closest('tr').dataset.mission
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
      this.changeURLGivenChecks(
        this.groupActions.querySelector('#export-pdf'),
        checkeds
      )
      if (checkedsLength >= 2 && this.batchAmendementsLink) {
        this.changeURLGivenChecks(this.batchAmendementsLink, checkeds)
      }
    }

    changeURLGivenChecks(target, checkeds) {
      const url = new URL(target.getAttribute('href'))
      url.searchParams.delete('nums')
      checkeds.forEach(checked => {
        url.searchParams.append('nums', checked.value)
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

application.register(
  'amendements-articles',
  class extends Stimulus.Controller {
    static get targets() {
      return ['list']
    }
    toggle(event) {
      this.listTarget.classList.toggle('d-none')
      this.element.scrollIntoView()
      event.preventDefault()
    }
  }
)

class AmendementsFilters extends Stimulus.Controller {
  static get targets() {
    return [
      'row',
      'link',
      'bottom',
      'count',
      'table',
      'tbody',
      'articleInput',
      'missionInput',
      'amendementInput',
      'gouvernementalCheckbox',
      'gouvernementalLabel',
      'tableInput',
      'emptytableCheckbox',
      'emptytableLabel'
    ]
  }

  initialize() {
    const articleFilter = this.getURLParam('article')
    if (articleFilter !== '') {
      this.toggle()
      this.articleInputTarget.value = articleFilter
      this.filterByArticle(articleFilter)
    }
    const missionFilter = this.getURLParam('mission')
    if (missionFilter !== '' && this.hasMissionInputTarget) {
      this.toggle()
      this.missionInputTarget.value = missionFilter
      this.filterByMission(missionFilter)
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
    const tableFilter = this.getURLParam('table')
    if (tableFilter !== '') {
      this.toggle()
      this.tableInputTarget.value = tableFilter
      this.filterByTable(tableFilter)
    }
    const emptytableFilter = this.getURLParam('emptytable')
    if (emptytableFilter !== '') {
      this.toggle()
      this.emptytableCheckboxTarget.checked = true
      this.emptytableLabelTarget.querySelector('abbr').classList.add('selected')
      this.filterByEmptytable(emptytableFilter)
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
      this.countTarget.innerHTML = `Aucun amendement (${initial} au total)`
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
      this.countTarget.innerHTML = `${current} amendement${plural}`
    else
      this.countTarget.innerHTML = `${current} amendement${plural} (${initial} au total)`
  }

  filterArticle(event) {
    const value = event.target.value.trim()
    this.filterByArticle(value)
    this.setURLParam('article', value)
    this.updateCount()
  }

  filterMission(event) {
    const value = event.target.value.trim()
    this.filterByMission(value)
    this.setURLParam('mission', value)
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

  filterTable(event) {
    const value = event.target.value.trim()
    this.filterByTable(value)
    this.setURLParam('table', value)
    this.updateCount()
  }

  filterEmptytable(event) {
    const checked = event.target.checked
    const value = checked ? '1' : ''
    this.emptytableLabelTarget
      .querySelector('abbr')
      .classList.toggle('selected', checked)
    this.filterByEmptytable(value)
    this.setURLParam('emptytable', value)
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

  filterByMission(value) {
    this.filterColumn('hidden-mission', line => {
      if (!value) {
        return true
      }
      return line.dataset.mission.startsWith(value.toLowerCase())
    })
  }

  filterByAmendement(value) {
    this.filterColumn('hidden-amendement', line => {
      if (!value) {
        return true
      }
      return line.dataset.amendement.split(',').some(num => num === value)
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

  filterByTable(value) {
    this.filterColumn('hidden-table', line => {
      if (!value) {
        return true
      }
      return line.dataset.table.toLowerCase().includes(value.toLowerCase())
    })
    this.tableTarget.classList.toggle('filtered-table', value)
  }

  filterByEmptytable(value) {
    this.filterColumn('hidden-emptytable', line => {
      if (!value) {
        return true
      }
      return line.dataset.emptytable.trim() === value
    })
    this.tableTarget.classList.toggle('filtered-emptytable', value)
  }

  filterColumn(className, shouldShow) {
    this.tbodyTarget.querySelectorAll('tr').forEach(line => {
      line.classList.toggle(className, !shouldShow(line))
    })
  }
}

application.register(
  'multiple-clicks',
  class extends Stimulus.Controller {
    prevent(event) {
      event.target.classList.add('disabled')
      const initialInnerHTML = event.target.innerHTML
      event.target.innerHTML = 'En cours de traitement…'
      window.setTimeout(_ => {
        event.target.innerHTML = initialInnerHTML
        event.target.classList.remove('disabled')
      }, 1000 * 10) // Seconds.
    }
  }
)

application.register(
  'filename',
  class extends Stimulus.Controller {
    display(event) {
      const input = event.target
      const filename = input.files[0].name
      const label = this.element.querySelector('label[for="' + input.id + '"]')
      label.innerHTML = filename
    }
  }
)
