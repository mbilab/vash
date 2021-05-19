import Vue from 'vue'
import Vuex from 'vuex'

import actions from './actions'
import config from '../config'

Vue.use(Vuex)

const _parseColumns = raw => {
  const ret = { columnGroups: {}, columnNames: [], columns: {} }
  for (const group in raw) {
    ret.columnGroups[group] = []
    for (const column of raw[group]) {
      if (column.visible == true) {
        column.group = group
        ret.columnGroups[group].push(column.name)
        ret.columnNames.push(column.name)
        ret.columns[column.name] = column
      }
    }
  }
  ret.filters = _resetFilters(ret.columns)
  return ret
}

const _resetFilter = column => {
  const filter = { filtered: false }

  if (column.position) filter.position = []
  if (column.contain) filter.contain = []

  if (column.equality) {
    filter.equality = column.equality
    filter.threshold = column.threshold || 0
  }

  if (column.equalTo) {
    const equalTo = []
    for (const obj of column.equalTo) {
      for (const key in obj) {
        equalTo.push({ [key]: true })
      }
    }
    filter.equalTo = equalTo
  }
  return filter
}

const _resetFilters = columns => {
  const filters = { '': {} }
  for (const column of Object.values(columns)) {
    const filter = _resetFilter(column)
    filters[column.name] = filter
  }
  return filters
}

export default new Vuex.Store({
  actions,

  getters: {
    filtered: (state, getters) => {
      if (getters.cohort.info)
        return JSON.parse(getters.cohort.info).filtered || []
      return []
    },
    filterDetails: state => {
      const detail = []
      for (const k in state.filters) {
        const filter = state.filters[k]

        if (!filter.filtered) continue
        if (filter.equality && filter.equality != '?')
          detail.push({
            name: k,
            detail: `${k} ${filter.equality} ${filter.threshold}`
          })

        if (filter.equalTo) {
          const values = filter.equalTo
            .filter(v => Object.values(v)[0])
            .map(v => Object.keys(v)[0])
          if (values.length && values.length < filter.equalTo.length)
            detail.push({
              name: k,
              detail: `${k}: ${values.join(', ')}`
            })
        }

        if (filter.contain && filter.contain.length) {
          detail.push({
            name: k,
            detail: `${k}: ${filter.contain.join(', ')}`
          })
        }
        if (filter.position && filter.position.length) {
          detail.push({
            name: k,
            detail: `${k}: ${filter.position.join(', ')}`
          })
        }
      }
      return detail
    },
    selectedColumns: state =>
      Object.fromEntries(
        Object.entries(state.columns).filter(([key, value]) => value.selected)
      ),
    loggedIn: state => state.user.id,
    nRequests: state => Object.keys(state.requests).length,
    getInfoById: state => id => JSON.parse(state.user.cohorts[id].info),
    cohort: state => {
      if (state.selectedCohortIdx == null) return {}
      return state.user.cohorts[state.selectedCohortIdx]
    },
    sampleBamFiles: state => {
      if (state.selectedCohortIdx == null) return {}
      let cohort = state.user.cohorts[state.selectedCohortIdx]
      let info = JSON.parse(cohort.info)
      let bamFiles = info['bam'].split(',')

      let samples = cohort.samples
      samples = samples.split(',')
      if (samples.length < 0) {
        return {}
      }

      let sampleBamFiles = {}
      for (let i in samples) {
        for (let file of bamFiles) {
          if (file != '' && samples[i] != '' && file.search(samples[i]) != -1) {
            sampleBamFiles[samples[i]] = file
          }
        }
      }

      return sampleBamFiles
    }
  },

  mutations: {
    addRequest: (state, { k, v }) => Vue.set(state.requests, k, v),
    delRequest: (state, k) => Vue.delete(state.requests, k),
    resetFilter: (state, columnName) => {
      Vue.set(
        state.filters,
        columnName,
        _resetFilter(state.columns[columnName])
      )
    },
    resetFilters: state =>
      Vue.set(state, 'filters', _resetFilters(state.columns)),
    resetStagedFilters: state => {
      state.stagedFilters = ['Add a column']
    },
    resetStagedFilter: (state, { idx, filterList }) => {
      let filterName = state.stagedFilters[idx]

      let filterReset = state.filters[filterName]
      if (filterReset.contain) {
        Vue.set(filterReset, 'contain', [])
      } else if (filterReset.position) {
        Vue.set(filterReset, 'position', [])
      } else if (filterReset.equality) {
        filterReset.equality = '?'
        filterReset.threshold = 100
      } else if (filterReset.equalTo) {
        for (let row of filterReset.equalTo) {
          Object.keys(row).forEach(v => (row[v] = true))
        }
      }
      filterReset.filtered = false

      state.stagedFilters.splice(idx, 1, `${filterName} has been reset`)
    },
    setCurrentpanel: (state, idx) => {
      state.currentPanel = state.panels[idx] || null
    },
    setStagedFilters: (state, { idx, column }) => {
      if (state.stagedFilters.includes(column)) return

      Vue.set(state.stagedFilters, idx, column)
      if (idx == state.stagedFilters.length - 1) {
        Vue.set(state.stagedFilters, idx + 1, 'Add a column')
      }

      const resetIdx = state.stagedFilters.indexOf(`${column} has been reset`)
      if (resetIdx < 0) return
      state.stagedFilters.splice(resetIdx, 1)
    },
    selectFilterColumn: (state, { name, selected }) => {
      state.columns[name].selected = selected
    },
    setCohortNLoaded: (state, { idx, nLoaded }) => {
      Vue.set(state.user.cohorts[idx], 'n_loaded_variants', nLoaded)
    },
    setCohortNVariants: (state, { idx, nVariants }) => {
      Vue.set(state.user.cohorts[idx], 'n_variants', nVariants)
    },

    setCohortSamples: (state, { samples }) => {
      let cohort = state.user.cohorts[state.selectedCohortIdx]
      let others = cohort.others
      let availables = cohort.available
      var scores = []
      if (availables) {
        availables = availables.split(',')
        scores = availables.filter(v => Object.keys(config.bScore).includes(v))
        availables = availables.filter(v => !scores.includes(v))

        const ret = { columnGroups: {}, columnNames: [], columns: {} } // reparse config
        let alleleFrequency = []
        for (var group in config.columns) {
          ret.columnGroups[group] = []
          for (var column of config.columns[group]) {
            if (availables.includes(column.name) || column.visible == true) {
              // if column shown or visible
              column.group = group
              ret.columnGroups[group].push(column.name)
              ret.columnNames.push(column.name)
              ret.columns[column.name] = column
            }
          }
        }
        state.columnNames = ret.columnNames
        state.columns = ret.columns
        state.filters = ret.filters
        state.columnGroups = ret.columnGroups
        for (let i in scores) {
          state.columnNames.push(scores[i])
          Vue.set(state.columns, scores[i], config.bScore[scores[i]])
          state.columnGroups['score'].push(scores[i]) // multiple group
        }
        state.filters = _resetFilters(state.columns)
      }
      samples = cohort.samples
      if (samples.length > 0) {
        samples = samples.split(',')
        state.columnGroups['samples'] = []
        for (let i in samples) {
          state.columnNames.splice(9 + parseInt(i), 0, samples[i])
          Vue.set(state.columns, samples[i], {
            filterable: false,
            group: 'samples',
            name: samples[i],
            selected: true,
            visible: true
          })
          state.columnGroups['samples'].push(samples[i])
          Vue.set(state.filters, samples[i], { filtered: false })
        }
      }
      if (others) {
        others = others.split(',')
        state.columnGroups['others'] = []
        // for (let i = 0; i <= parseInt(others.length / 20); i++) {
        //   state.columnGroups['others'][i] = []
        // }
        for (let i in others) {
          state.columnNames.push(others[i])
          Vue.set(state.columns, others[i], {
            filterable: false,
            group: 'others',
            name: others[i],
            selected: false,
            visible: true
          })
          state.columnGroups['others'].push(others[i])
          Vue.set(state.filters, others[i], { filtered: false })
        }
      }
    },

    setSelectedCohortIdx: (state, id) => {
      state.selectedCohortIdx = id
    },

    setCohortPid: (state, { idx, pid }) => {
      state.user.cohorts[idx].pid = pid
    },

    setCohortFilters: (state, { queries }) => {
      Vue.set(state.user.cohorts, state.selectedCohortIdx, {
        ...state.user.cohorts[state.selectedCohortIdx],
        n_variants: undefined,
        queries
      })
    },

    setCohortSubpanel: (state, v) => (state.cohortSubpanel = v),

    setLayout: (state, v) => (state.layout = v),

    setLoginError: (state, v) => (state.loginError = v),

    setFriends: (state, friends) => {
      Vue.set(state, 'friends', [...friends])
    },

    setTimeID: (state, id) => {
      state.timeID = id
    },

    setUser: (state, v) => (state.user = v),

    setUserCohort: (state, { idx, update_obj }) => {
      const cohorts = state.user.cohorts
      cohorts[idx] = { ...cohorts?.[idx], ...update_obj }
      Vue.set(state.user, 'cohorts', [...cohorts])
    }
  },

  state: {
    ..._parseColumns(config.columns),
    panels: ['cohort', 'column', 'filter', 'subCohort'],
    currentPanel: null,
    activeColumnName: 'Select a Filter',
    cohortSubpanel: 'list',
    filterSubpanel: 'editor',
    layout: 'vertical',
    loginError: '',
    requests: {},
    selectedCohortIdx: null,
    stagedFilters: ['Add a column'],
    timeID: null,
    user: {},
    friends: []
  }
})
