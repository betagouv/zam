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
function getSortSpecFromURL() {
    return getURLParam('sort')
}
function replaceSortSpecInURL(sortSpec) {
    setURLParam('sort', sortSpec)
}
function updateSortSpec(sortSpec, colSpec) {
    const updatedSpec = sortSpec
        .split('-')
        .filter(item => item !== '' && item.charAt(0) !== colSpec.charAt(0))
    updatedSpec.push(colSpec)
    return updatedSpec.join('-')
}

function makeHeadersSortable(tableHead) {
    tableHead.addEventListener('click', e => {
        let tableHeader = e.target
        if (
            tableHeader.classList.contains('nosort') ||
            tableHeader.nodeName === 'INPUT' ||
            tableHeader.nodeName === 'OPTION' ||
            tableHeader.nodeName === 'SELECT'
        )
            return
        if (tableHeader.nodeName === 'use') tableHeader = tableHeader.parentNode
        if (tableHeader.nodeName === 'svg') tableHeader = tableHeader.parentNode
        const isAscending = tableHeader.getAttribute('data-order') === 'asc'
        const order = isAscending ? 'desc' : 'asc'

        const tableHeaders = tableHead.querySelectorAll('tr.headers th')
        const colIndex =
            Array.prototype.indexOf.call(tableHeaders, tableHeader) + 1
        sortSpec = updateSortSpec(getSortSpecFromURL(), colIndex + order)
        replaceSortSpecInURL(sortSpec)
        sortColumn(tableHeader, colIndex, order)
    })
}
function sortColumns(sortSpec) {
    for (colSpec of sortSpec.split('-')) {
        const colIndex = parseInt(colSpec.charAt(0), 10)
        if (colIndex < 2 || colIndex > 6) {
            continue
        }
        const order = colSpec.slice(1)
        if (order !== 'asc' && order !== 'desc') {
            continue
        }
        const tableHeader = document.querySelector(
            'thead tr:first-child th:nth-child(' + colIndex + ')'
        )
        sortColumn(tableHeader, colIndex, order)
    }
}
function sortColumn(tableHeader, colIndex, order) {
    tableHeader.setAttribute('data-order', order)
    const selector = 'td:nth-child(' + colIndex + ')'
    tableHeader
        .querySelector('svg use')
        .setAttribute('xlink:href', '#sort-' + order)
    const options = {
        sortFunction: (a, b) => {
            return compareArrays(
                extractItems(a.elm, selector),
                extractItems(b.elm, selector)
            )
        },
        order: order
    }
    tinysort(document.querySelectorAll('tbody tr'), options)
    document.querySelector('table').classList.add('sorted')
}
function extractItems(elem, selector) {
    const value = elem.querySelector(selector).dataset.sortkey
    return value.split('|').map(maybeNumber)
}
function maybeNumber(value) {
    const number = parseInt(value, 10)
    if (isNaN(number)) {
        return value
    }
    return number
}
function compareArrays(a, b) {
    const length = Math.min(a.length, b.length)
    for (let i = 0; i < length; i++) {
        const elA = a[i],
            elB = b[i]
        if (elA > elB) {
            return 1
        }
        if (elA < elB) {
            return -1
        }
    }
    return b.length - a.length
}
function sortColumnsFromQueryString() {
    const sortSpec = getSortSpecFromURL()
    if (sortSpec !== '') {
        sortColumns(sortSpec)
    }
}
function allowUnsort(tableHead) {
    document.querySelector('#unsort').addEventListener('click', e => {
        e.preventDefault()
        Array.from(tableHead.querySelectorAll('th[data-order]')).forEach(th => {
            th.removeAttribute('data-order')
        })
        setURLParam('sort', '')
        tinysort(document.querySelectorAll('tbody tr'), { data: 'order' })
        document.querySelector('table').classList.remove('sorted')
    })
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

function takeControlOverNativeJump() {
    /* To avoid position under sticky headers. */
    if (location.hash) {
        /* Waiting for the next tick to supplement previous browser behavior. */
        setTimeout(() => {
            const element = document.querySelector(window.location.hash)
            const target = element.getBoundingClientRect()
            window.scrollTo({
                /* Position the highlighted element in the middle of the page. */
                top: window.scrollY + target.top - window.innerHeight / 2,
                behavior: 'smooth'
            })
        }, 1)
    }
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
            if (checkeds.length < 1) {
                this.groupActions.classList.add('d-none')
                document
                    .querySelectorAll('tr.headers th')
                    .forEach(th => (th.style.top = '0'))
                document
                    .querySelectorAll('tr.filters th')
                    .forEach(th => (th.style.top = '2rem'))
            } else {
                this.groupActions.classList.remove('d-none')
                document
                    .querySelectorAll('tr.headers th')
                    .forEach(th => (th.style.top = '3rem'))
                document
                    .querySelectorAll('tr.filters th')
                    .forEach(th => (th.style.top = '5rem'))
            }
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
    'amendements-options',
    class extends Stimulus.Controller {
        static get targets() {
            return ['details']
        }
        toggle(event) {
            this.detailsTarget.classList.toggle('d-none')
            event.target.classList.toggle('enabled')
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
