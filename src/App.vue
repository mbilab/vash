<template lang="pug">
#v-app
  login-page#login-page(v-if='!loggedIn')
  .-viewer(v-else)
    app-header
    .ui.red.label(v-show='nRequests') {{ nRequests }} pending requests...
    .-app-content
      side-panel.-viewer-side-panel
      big-table.-viewer-table
</template>

<script>
import 'semantic-ui-offline/semantic.css'
import VueSmoothReflow from 'vue-smooth-reflow'
import { mapActions, mapState, mapGetters, mapMutations } from 'vuex'
export default {
  components: {
    'login-page': require('./components/LoginPage.vue').default,
    'app-header': require('./components/AppHeader.vue').default,
    'side-panel': require('./components/SidePanel.vue').default,
    'big-table': require('./components/BigTable.vue').default
  },

  computed: {
    ...mapState(['filters', 'panels', 'currentPanel']),
    ...mapGetters(['loggedIn', 'nRequests'])
  },

  created() {
    this.me()
  },

  methods: {
    ...mapActions(['me']),
    ...mapMutations(['setCurrentpanel'])
  },

  mixins: [VueSmoothReflow],

  mounted() {
    this.$smoothReflow({ el: '#login-page', transition: 'height .2s' })
  }
}
</script>

<style lang="sass">
*
  margin: 0
  padding: 0
  box-sizing: border-box
</style>

<style lang="sass" scoped>
@import "./assets/variables.sass"

$header-bottom-border: 2px solid rgba(34, 36, 38, 0.15)
$tittle-color: $LIGHT-COLOR-4
$header-color: $DARK-COLOR-2

#v-app
  background-color: $LIGHT-COLOR-5
.-viewer
  width: 100vw
  top: 0px
  display: flex
  flex-direction: column
  height: calc(100% - 1em)
  .ui.red.label
    position: absolute
    left: 50%
    transform: translateX(-50%)

.-app-content
  width: 100vw
  top: 0px
  display: flex
  height: calc(100% - 64px)

.-viewer-side-panel, .-viewer-table
  height: calc(100vh - #{$HEADER-HEIGHT})

@keyframes blinker
  50%
    color: rgba(255, 255, 255, .5)
</style>
// }}}
