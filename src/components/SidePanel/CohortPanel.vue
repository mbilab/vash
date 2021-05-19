<template lang="pug">
.-cohort-panel
  keep-alive
    component(:is="currentPanelComponent", @changeComponent="changeComponent", :cohort-idx='cohortIdx')
</template>

<script>
import 'semantic-ui-offline/semantic.css'
export default {
  components: {
    'cohort-list': require('./CohortPanel/CohortList.vue').default,
    'cohort-creator': require('./CohortPanel/CohortCreator.vue').default,
    'cohort-editor': require('./CohortPanel/CohortEditor.vue').default,
    'sharing-editor': require('./CohortPanel/SharingEditor.vue').default
  },
  data() {
    return {
      currentPanelComponent: 'cohort-list',
      cohortIdx: null
    }
  },
  methods: {
    changeComponent(component, cohortIdx = null) {
      this.currentPanelComponent = component
      this.cohortIdx = cohortIdx
    }
  }
}
</script>

<style lang="sass" scoped>
@import "~@/assets/variables.sass"

.-cohort-panel
  padding: 1em
  height: 100%
  width: $SIDE-PANEL-COMPONENT-WIDTH
  position: relative
  background-color: $LIGHT-COLOR-5
  border-right: $BORDER

.animating.dimmable:not(body), .dimmed.dimmable:not(body)
  overflow: visible
</style>
