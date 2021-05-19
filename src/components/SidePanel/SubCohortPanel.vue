<template lang="pug">
.-subcohort-panel
  div
    h3 Save a Subcohort
    .ui.form
      .field
        label Cohort Name
        input(type="text",v-model='cohortName')
      .field
        label Description
        textarea(type="text",v-model='description')
      .field
        label Filters
        .ui.labels
          .ui.label(v-for="filter in totalFilters", @click='activateFilter(filter.name)') {{ filter }}
  button.fluid.ui.button(@click='create', :class='{disabled: selectedCohortIdx==null }') Create new cohort
</template>

<script>
import 'semantic-ui-offline/semantic.css'
import { mapActions, mapGetters, mapState } from 'vuex'
export default {
  computed: {
    ...mapState(['filters', 'selectedCohortIdx']),
    ...mapGetters(['cohort', 'filtered', 'filterDetails']),
    totalFilters() {
      return this.filtered.concat(this.filterDetails.map(v => v.detail))
    }
  },

  data() {
    return {
      cohortName: '',
      description: '',
      bam: ''
    }
  },

  methods: {
    ...mapActions(['createSubCohort']),
    create() {
      this.createSubCohort({
        cohort_id: this.cohort.id,
        name: this.cohortName,
        description: this.description,
        bam: this.bam,
        filtered: this.totalFilters,
        n_variants: this.cohort.n_variants,
        queries: this.cohort.queries
      })
      // this.setFilterSubpanel('editor')
      // this.openPanel('Cohort')
    }
  }
}
</script>

<style lang="sass" scoped>
@import "~@/assets/variables.sass"

.-subcohort-panel
  padding: 1em
  height: 100%
  width: $SIDE-PANEL-COMPONENT-WIDTH
  position: relative

  background-color: $LIGHT-COLOR-5
  border-right: $BORDER
  height: 100%
  width: $SIDE-PANEL-COMPONENT-WIDTH
  margin: 0

  .field
    .label
      background-color: rgba(0,0,0,0.15)
</style>
