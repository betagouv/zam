function getURLParam(name) {
    const urlParams = new URLSearchParams(window.location.search)
    return urlParams.get(name) || ''
}
function setURLParam(name, value) {
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

function filterByArticle(value) {
    filterColumn('hidden-article', line => {
        if (!value) {
            return true
        }
        return line.dataset.article.trim() === value
    })
}
function filterByAmendement(value) {
    filterColumn('hidden-amendement', line => {
        if (!value) {
            return true
        }
        return line.dataset.amendement.trim() === value
    })
    document
        .querySelector('table')
        .classList.toggle('filtered-amendement', value)
}
function filterByTable(value) {
    filterColumn('hidden-table', line => {
        if (!value) {
            return true
        }
        return line.dataset.table.toLowerCase().includes(value.toLowerCase())
    })
    document.querySelector('table').classList.toggle('filtered-table', value)
}
function filterByAvis(value) {
    filterColumn('hidden-avis', line => {
        if (value === '') {
            return true
        }
        if (
            line.dataset.gouvernemental === '1' ||
            line.dataset.abandonedBeforeSeance === '1'
        ) {
            return false
        }
        return line.dataset.avis === value
    })
    document.querySelector('table').classList.toggle('filtered-avis', value)
}
function filterByReponse(value) {
    filterColumn('hidden-reponse', line => {
        if (value === '') {
            return true
        }
        return line.dataset.reponse === value
    })
    document.querySelector('table').classList.toggle('filtered-reponse', value)
}
function filterColumn(className, shouldShow) {
    Array.from(document.querySelectorAll('tbody tr')).forEach(line => {
        line.classList.toggle(className, !shouldShow(line))
    })
}
function showFilters() {
    document.querySelector('#toggle-filter').classList.add('enabled')
    document.querySelector('tr.filters').classList.remove('d-none')
}

function filterColumns(table) {
    table.querySelector('#article-filter').addEventListener('keyup', e => {
        const value = e.target.value.trim()
        filterByArticle(value)
        setURLParam('article', value)
    })
    table.querySelector('#amendement-filter').addEventListener('keyup', e => {
        const value = e.target.value.trim()
        filterByAmendement(value)
        setURLParam('amendement', value)
    })
    table.querySelector('#table-filter').addEventListener('keyup', e => {
        const value = e.target.value.trim()
        filterByTable(value)
        setURLParam('table', value)
    })
    table.querySelector('#avis-filter').addEventListener('change', e => {
        const value = e.target.value.trim()
        filterByAvis(value)
        setURLParam('avis', value)
    })
    table.querySelector('#reponse-filter').addEventListener('change', e => {
        const value = e.target.value.trim()
        filterByReponse(value)
        setURLParam('reponse', value)
    })

    const articleFilter = getURLParam('article')
    if (articleFilter !== '') {
        showFilters()
        document.querySelector('#article-filter').value = articleFilter
        filterByArticle(articleFilter)
    }
    const amendementFilter = getURLParam('amendement')
    if (amendementFilter !== '') {
        showFilters()
        document.querySelector('#amendement-filter').value = amendementFilter
        filterByAmendement(amendementFilter)
    }
    const tableFilter = getURLParam('table')
    if (tableFilter !== '') {
        showFilters()
        document.querySelector('#table-filter').value = tableFilter
        filterByTable(tableFilter)
    }
    const avisFilter = getURLParam('avis')
    if (avisFilter !== '') {
        showFilters()
        document.querySelector('#avis-filter').value = avisFilter
        filterByAvis(avisFilter)
    }
    const reponseFilter = getURLParam('reponse')
    if (reponseFilter !== '') {
        showFilters()
        document.querySelector('#reponse-filter').value = reponseFilter
        filterByReponse(reponseFilter)
    }
}

function hijackEditLinks() {
    /* To inject the current page URL as a "back" query param */
    const editLinks = document.querySelectorAll('a.edit-amendement')
    Array.from(editLinks).forEach(editLink => {
        editLink.addEventListener('click', e => {
            e.preventDefault()
            const thisURL = new URL(window.location.href)
            const linkURL = new URL(e.target.href)
            thisURL.hash = ''
            linkURL.searchParams.set('back', thisURL.pathname + thisURL.search)
            const href = linkURL.toString()
            if (
                e.ctrlKey ||
                e.shiftKey ||
                e.metaKey || // apple
                (e.button && e.button == 1) // middle click, >IE9 + everyone else
            ) {
                window.open(href).focus()
            } else {
                window.location.href = href
            }
        })
    })
}

application.register(
    'amendements-selection',
    class extends Stimulus.Controller {
        initialize() {
            this.groupActions = this.element.querySelector('.groupActions')
            this.selectAllCheckbox = this.element.querySelector(
                'input[type="checkbox"][name="select-all"]'
            )
            // Useful in case of (soft) refresh with already checked box.
            this.selectAllCheckbox.checked = false
            this.checkboxes = this.element.querySelectorAll(
                'input[type="checkbox"]:not([name="select-all"])'
            )
            // Useful in case of (soft) refresh with already checked boxes.
            this.toggleGroupActions()
            this.checkboxes.forEach(checkbox => {
                checkbox.addEventListener('change', e => {
                    this.toggleGroupActions()
                })
            })
        }

        toggleGroupActions() {
            const checkeds = Array.from(this.checkboxes).filter(
                box => box.checked
            )
            this.groupActions.classList.toggle('d-none', checkeds.length < 1)
            this.changeURLGivenChecks(
                this.groupActions.querySelector('#transfer-amendements'),
                checkeds
            )
            this.changeURLGivenChecks(
                this.groupActions.querySelector('#export-pdf'),
                checkeds
            )
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
                const display = getComputedStyle(
                    checkbox.parentElement.parentElement,
                    null
                ).display
                if (display != 'none') {
                    checkbox.checked = this.selectAllCheckbox.checked
                    // Required because the change event is not propagated by default.
                    const event = new Event('change')
                    checkbox.dispatchEvent(event)
                }
            })
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

application.register(
    'amendements-filters',
    class extends Stimulus.Controller {
        static get targets() {
            return ['row']
        }
        toggle(event) {
            this.rowTarget.classList.toggle('d-none')
            event.preventDefault()
        }
    }
)

application.register(
    'amendements-lecture',
    class extends Stimulus.Controller {
        delete(event) {
            if (
                window.confirm(
                    'Êtes-vous sûr·e de vouloir supprimer toutes les données ' +
                    'relatives à cette lecture incluant les avis et les réponses ?'
                )
            ) {
                return
            } else {
                event.preventDefault()
            }
        }
    }
)

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
