<template lang="pug">
.-side-panel(@keyup.esc='currentPanel=null' tabindex='0')
  .-side-bar
    .-buttons
      .-button(
        v-for='(panel, idx) in panels' :class='{"dark":panels[idx]==currentPanel}'
        @click='setCurrentpanel(currentPanel==panels[idx]?null:idx)'
        )
        button.circular.ui.icon.button
          i(:class='buttonIconMap[panels[idx]]').icon
        span {{ buttonTittleMap[panels[idx]] }}
  .-padding
  // https://vuejs.org/v2/guide/components.html#Dynamic-Components
  keep-alive
    component.-components(:class='{show: currentPanel!=null}' v-if='currentPanelComponent', :is="currentPanelComponent")

</template>

<script>
import 'semantic-ui-offline/semantic.css'
import { mapMutations, mapState } from 'vuex'

export default {
  mounted() {
    window.addEventListener('click', this.clickNoSidPanel, 1)
  },
  destroyed() {
    window.removeEventListener('click', this.clickNoSidPanel, 1)
  },
  components: {
    'cohort-panel': require('./SidePanel/CohortPanel.vue').default,
    'column-panel': require('./SidePanel/ColumnPanel.vue').default,
    'filter-panel': require('./SidePanel/FilterPanel.vue').default,
    'subCohort-panel': require('./SidePanel/SubCohortPanel.vue').default
  },
  computed: {
    ...mapState(['panels', 'currentPanel']),
    currentPanelComponent() {
      if (!this.currentPanel) return false
      return this.currentPanel + '-panel'
    }
  },

  data() {
    return {
      buttonIconMap: {
        cohort: 'list',
        column: 'th',
        filter: 'filter',
        subCohort: 'copy'
      },
      buttonTittleMap: {
        cohort: 'Cohort List',
        column: 'Columns',
        filter: 'Filters',
        subCohort: 'Save a Cohort'
      }
    }
  },

  methods: {
    ...mapMutations(['setCurrentpanel']),
    clickNoSidPanel: function(event) {
      let sidePanel = document.querySelector('.-side-panel')
      if (
        event.clientX < 0 ||
        sidePanel.offsetLeft + sidePanel.offsetWidth < event.clientX ||
        event.clientY < 0 ||
        sidePanel.offsetTop + sidePanel.offsetHeight < event.clientY
      )
        this.setCurrentpanel(-1)
    }
  }
}
</script>

<style lang="sass" scoped>
@import "~@/assets/variables.sass"
.-side-panel
  display: flex
.-components
  transition: clip-path .2s
  clip-path: inset(0 0 0 100%)

.-components.show
  clip-path: inset(0 0 0 0)

.-padding
  width: 60px
  height: calc(100vh - #{$HEADER-HEIGHT})

.-side-bar
  transition: clip-path .2s .2s
  clip-path: inset(0 13em 0 0)
  padding: 1em 0
  background-color: $LIGHT-COLOR-5
  position: fixed
  .-buttons
    display: flex
    flex-direction: column
    margin: 0 .7em
    .-button
      border-top-right-radius: 3em
      border-bottom-right-radius: 3em
      background-color: $LIGHT-COLOR-5
      button
        background-color: $LIGHT-COLOR-5
        i
          color: $DARK-COLOR-3
    .-button.dark
      button
        background-color: $LIGHT-COLOR-1
        i
          color: $MAJOR-COLOR-1
  overflow: hidden
  height: calc(100vh - #{$HEADER-HEIGHT})
  z-index: 100
  span
    margin: 1em 5em 1em 1em
    opacity: 0

.-side-bar:hover
  clip-path: inset(0 -10% 0 0)
  border-right: $BORDER
  box-shadow: rgba(184, 194, 215, 0.5) 3px 0px 6px 0px
  .-button:hover
    background-color: $LIGHT-COLOR-3
    button
      background-color: $LIGHT-COLOR-3
  .-button.dark
    background-color: $LIGHT-COLOR-1
    button
      background-color: $LIGHT-COLOR-1
  span
    opacity: 1
</style>
