import Vue from 'vue'

import App from './App.vue'
import store from './store'
import { runMockingServer } from './mock-server'

if (process.env.VUE_APP_USE_MOCKING == 'true') {
  runMockingServer()
}

new Vue({
  el: '#app',
  render: h => h(App),
  store
})
