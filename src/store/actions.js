import axios from 'axios'
import 'babel-polyfill' // for async/await
import localforage from 'localforage'
import { debounce, throttle } from 'lodash'

import config from '../config'
// import mock from '../mock'

axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

const _cachedGet = async ({ commit, key, param, url }) => {
  if (!key) key = url
  const cache = await localforage.getItem(key)
  if (cache) return cache
  const timestamp = Date.now()
  commit('addRequest', { k: timestamp, v: true })
  const { data } = await axios.post(url, param)
  await localforage.setItem(key, data)
  commit('delRequest', timestamp)
  return data
}

const activateFilter = async ({ commit, state }, filterName) => {
  if (!state.columns[filterName].filterable) return
  const filterPanelIdx = state.panels.indexOf('filter')
  commit('setCurrentpanel', filterPanelIdx)
  commit('setStagedFilters', {
    idx: state.stagedFilters.length - 1,
    column: filterName
  })
}

const getCohort = async ({ commit, state }, { id, queries }) => {
  const url = `/cohort/${id}/`

  const timestamp = Date.now()
  commit('addRequest', { k: timestamp, v: true })
  let param = { queries }
  const { data } = await axios.post(url, param)
  commit('delRequest', timestamp)

  return data
}

const getVariants = (
  { commit, state },
  { start, size, id_query, reverse = false, match_counts = {} }
) => {
  //
  // return [data, error]
  //
  if (state.selectedCohortIdx === null) return [null, 'cohortIdx not selected']
  if (Number.isNaN(size)) return [null, 'size is NaN']
  const cohort = state.user.cohorts[state.selectedCohortIdx]
  const timestamp = Date.now()
  const id = cohort.id
  let queries = cohort.queries
  if (id_query) {
    queries = JSON.parse(queries)
    queries.push(id_query)
    queries = JSON.stringify(queries)
  }
  match_counts = JSON.stringify(match_counts)
  commit('addRequest', { k: timestamp, v: { start } })
  let startTime = Date.now()
  const { data } = await axios.post(`/variants/${id}/${start}/${size}/`, {
    queries,
    reverse,
    match_counts
  })
}

const getFriends = async ({ commit, state }) => {
  const { data } = await axios.get('/friends/')
  commit('setFriends', data.friends)
}

const getTerms = async ({ commit, state }, { dbName, keyword }) => {
  const cohort = state.user.cohorts[state.selectedCohortIdx]
  if (!cohort) return []
  try {
    var { data } = await axios.post(`/terms/${cohort.id}/`, {
      dbName,
      keyword
    })
  } catch (error) {
    return []
  }
  return data
}

const deleteCohort = async ({ commit, state }, idx) => {
  let check = confirm(
    `Are you sure you want to delete the cohort:${state.user.cohorts[idx].name}?`
  )
  if (check) {
    axios.post(`/cohort/delete/${state.user.cohorts[idx].id}/`)
    commit('setCohortPid', { idx, pid: 2 })
  }
}

const updateUserCohort = async ({ commit, state }, { idx, update_obj }) => {
  axios.post(
    `/cohort/update/${state.user.cohorts[idx].id}/`,
    JSON.stringify({ update_obj })
  )
  commit('setUserCohort', { idx, update_obj })
}

const login = async ({ commit, dispatch }, params) => {
  const { data } = await axios.post('/login/', params)
  if (data.error) {
    commit('setLoginError', data.error)
    commit('setUser', {})
  } else commit('setUser', data)
}

const logout = ({ commit }) => {
  commit('setCohort', {})
  commit('setUser', {})
  axios.get('/logout')
}

const me = async ({ commit, dispatch, state }) => {
  const { data } = await axios.post('/me/')
  commit('setUser', data.error ? {} : { ...data })
}

const appendUserCohort = async ({ commit, dispatch, state }, idx) => {
  const { data } = await axios.post('/me/')
  commit('setUserCohort', { idx: idx, update_obj: data.cohorts[idx] })
}

export default {
  async createCohort({ commit, dispatch, state }, params) {
    const timestamp = Date.now()
    commit('addRequest', { k: timestamp, v: true })
    const { data } = await axios.post('/cohort/create/', params)
    commit('delRequest', timestamp)
    await dispatch('appendUserCohort', state.user.cohorts.length)
  },

  async createSubCohort({ commit, dispatch, state }, params) {
    const timestamp = Date.now()
    commit('addRequest', { k: timestamp, v: true })
    const { data } = await axios.post('/cohort/create/sub/', params)
    commit('delRequest', timestamp)
    await dispatch('appendUserCohort', state.user.cohorts.length)
  },

  getCacheItem: async ({}, { key }) => await localforage.getItem(key),

  activateFilter,
  getCohort,
  getFriends,
  getTerms,
  getVariants,
  deleteCohort,
  updateUserCohort,
  login,
  logout,
  me,
  appendUserCohort,

  async setCacheItem({}, { key, value }) {
    await localforage.setItem(key, value)
  }
}
