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
                if (checkbox.offsetParent !== null) {
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
            return [
                'row',
                'link',
                'count',
                'table',
                'tbody',
                'articleInput',
                'amendementInput',
                'tableInput',
                'avisSelect',
                'reponseSelect'
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
            const tableFilter = this.getURLParam('table')
            if (tableFilter !== '') {
                this.toggle()
                this.tableInputTarget.value = tableFilter
                this.filterByTable(tableFilter)
            }
            const avisFilter = this.getURLParam('avis')
            if (avisFilter !== '') {
                this.toggle()
                this.avisSelectTarget.value = avisFilter
                this.filterByAvis(avisFilter)
            }
            const reponseFilter = this.getURLParam('reponse')
            if (reponseFilter !== '') {
                this.toggle()
                this.reponseSelectTarget.value = reponseFilter
                this.filterByReponse(reponseFilter)
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
                window.history.replaceState(
                    { path: newURL.href },
                    '',
                    newURL.href
                )
            }
        }

        toggle(event) {
            this.linkTarget.classList.toggle('enabled')
            this.rowTarget.classList.toggle('d-none')
            if (event) event.preventDefault()
        }

        updateCount() {
            const initial = parseInt(this.data.get('initial-count'))
            const current = this.tbodyTarget.querySelectorAll(
                'tr:not([class^=hidden])'
            ).length
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

        filterAmendement(event) {
            const value = event.target.value.trim()
            this.filterByAmendement(value)
            this.setURLParam('amendement', value)
            this.updateCount()
        }

        filterTable(event) {
            const value = event.target.value.trim()
            this.filterByTable(value)
            this.setURLParam('table', value)
            this.updateCount()
        }

        filterAvis(event) {
            const value = event.target.value.trim()
            this.filterByAvis(value)
            this.setURLParam('avis', value)
            this.updateCount()
        }

        filterReponse(event) {
            const value = event.target.value.trim()
            this.filterByReponse(value)
            this.setURLParam('reponse', value)
            this.updateCount()
        }

        filterByArticle(value) {
            this.filterColumn('hidden-article', line => {
                if (!value) {
                    return true
                }
                return line.dataset.article.trim() === value
            })
        }

        filterByAmendement(value) {
            this.filterColumn('hidden-amendement', line => {
                if (!value) {
                    return true
                }
                return line.dataset.amendement.trim() === value
            })
            this.tableTarget.classList.toggle('filtered-amendement', value)
        }

        filterByTable(value) {
            this.filterColumn('hidden-table', line => {
                if (!value) {
                    return true
                }
                return line.dataset.table
                    .toLowerCase()
                    .includes(value.toLowerCase())
            })
            this.tableTarget.classList.toggle('filtered-table', value)
        }

        filterByAvis(value) {
            this.filterColumn('hidden-avis', line => {
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
            this.tableTarget.classList.toggle('filtered-avis', value)
        }

        filterByReponse(value) {
            this.filterColumn('hidden-reponse', line => {
                if (value === '') {
                    return true
                }
                return line.dataset.reponse === value
            })
            this.tableTarget.classList.toggle('filtered-reponse', value)
        }

        filterColumn(className, shouldShow) {
            this.tbodyTarget.querySelectorAll('tr').forEach(line => {
                line.classList.toggle(className, !shouldShow(line))
            })
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
            const label = this.element.querySelector(
                'label[for="' + input.id + '"]'
            )
            label.innerHTML = filename
        }
    }
)
