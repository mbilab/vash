<template lang="pug">
.-cohort-list
  .-title.-flex-container
    h3 Cohort List
    i.plus.icon(@click="$emit('changeComponent', 'cohort-creator')")
  .-cohort-each.ui.divided.list
    .item(
      v-for='(cohort, idx) in user.cohorts',
      :class="{open: openedCohortIdx == idx, selected: selectedCohortIdx == idx}",
      tabindex=0
      @click="toggleCohort(idx)",
      @keyup.enter="load(idx)"
    )
      .-cohort-name.-flex-container
        h4.ui.header
          i.large.users.icon
          .content {{ cohort.name }}
            .sub.header {{ getParentDescription(cohort.id, cohort.parent_cohort_id) }}
        div
          span(v-if='cohort.pid==0') {{ fromNow(cohort.ctime) }}
          span(v-if='cohort.pid==1') creating: {{ cohort.created_percentage.toFixed(1) }} %
          span(v-if='cohort.pid==2') deleted
          .ui.mini.basic.circular.icon.simple.dropdown.button(@click.stop)
            i.ellipsis.vertical.icon
            .menu
              .item(@click="$emit('changeComponent', 'cohort-editor', idx)")
                i.file.alternate.outline.icon
                span Edit Cohort
              .item(@click="$emit('changeComponent', 'sharing-editor', idx)")
                i.share.icon
                span Edit Sohort Sharing
      .-addition
        .ui.divider
        .-details
          h5 Descriptions
          p {{ JSON.parse(cohort.info)['description']['detail'] }}
          p(v-if='!JSON.parse(cohort.info)["description"]["detail"]') No description
          h5 BAM Files
          ul
            li(v-for="bam in JSON.parse(cohort.info)['bam'].split(',')" v-show="bam") {{ bam }}
          p(v-if='!JSON.parse(cohort.info)["bam"]') No BAM file
          h5 Applied Filter
          .ui.mini.labels
            .ui.label(v-for="filter in JSON.parse(cohort.info)['filtered']") {{ filter }}
          p(v-if='!JSON.parse(cohort.info)["filtered"]') No applied filter
      .-hinter
  button.ui.major.button.-load(@click='load(openedCohortIdx)', :class='{disabled: !cohortBuilt }') Load
</template>

<script>
import { DateTime } from 'luxon'
import 'semantic-ui-offline/semantic.css'
import { mapState, mapActions, mapMutations, mapGetters } from 'vuex'
export default {
  mounted() {
    this.$root.$on('CohortList:update', this.updateCohortsPeriodcally)
  },
  activated() {
    this.updateCohortsPeriodcally()
  },

  deactivated() {
    window.clearInterval(this.timer)
  },

  data() {
    return {
      openedCohortIdx: null,
      timer: null
    }
  },

  computed: {
    ...mapGetters(['cohort']),
    ...mapState(['user', 'selectedCohortIdx']),
    cohortBuilt() {
      return this.user?.cohorts?.[this.openedCohortIdx]?.pid == 0
    }
  },

  methods: {
    ...mapActions(['getCohort']),
    ...mapMutations([
      'resetFilters',
      'setSelectedCohortIdx',
      'setUserCohort',
      'setCohortNLoaded',
      'setCohortNVariants',
      'setCohortPid',
      'setTimeID'
    ]),

    toggleCohort(idx) {
      this.openedCohortIdx = this.openedCohortIdx == idx ? null : idx
    },
    getParentDescription(childId, parentId) {
      let parent = this.user.cohorts.find(cohort => cohort.id == parentId)
      return parentId == null || childId == parentId
        ? 'Original Cohort'
        : 'Filtered From: ' + parent.name
    },
    // idx of this cohortList
    load(idx) {
      if (!this.cohortBuilt) return
      if (idx == null) return
      this.setSelectedCohortIdx(idx)
      this.resetFilters()
      this.$root.$emit('BigTable:reset')
    },

    updateCohortsPeriodcally() {
      this.updateCohort()
      this.timer = window.setInterval(() => {
        this.updateCohort()
      }, 2000)
    },

    fromNow(time) {
      return DateTime.fromISO(time).toRelative({ locale: 'en' })
    },

    allCohortCreated() {
      return true
    },

    async updateCohort() {
      let updatedCohorts = this.user.cohorts.map(async cohort => {
        if (cohort.pid == 0) return 0

        return await this.getCohort({
          id: cohort.id,
          queries: cohort.queries
        })
      })

      Promise.all(updatedCohorts).then(cohorts => {
        let allCohortCreated = cohorts.every(
          cohort => cohort.pid == 0 || cohort == 0
        )

        cohorts.forEach((cohort, index) => {
          if (cohort == 0) return
          let update_obj = {
            available: cohort.available,
            created_percentage: cohort.created_percentage,
            n_variants: cohort.n_variants,
            samples: cohort.samples,
            pid: cohort.pid
          }
          this.setUserCohort({ idx: index, update_obj: update_obj })
        })

        if (allCohortCreated) {
          window.clearInterval(this.timer)
        }
      })
    }
  }
}
</script>

<style lang="sass" scoped>
@import "~@/assets/variables.sass"

.major.button
  background-color: $MAJOR-COLOR-1
  color: $LIGHT-COLOR-3


.-cohort-list
  height: 100%
  position: relative
  .-flex-container
    display: flex
    justify-content: space-between
    align-items: center
  .-title
    margin-bottom: 1em
    h3
      margin: 0
    .icon
      margin: 0 0 0.3em 0
      cursor: pointer
  .-cohort-each
    height: 80vh
    overflow: auto
    >.item
      border: $BORDER
      border-radius: .5em
      box-shadow: rgba(184, 194, 215, 0.35) 0px 3px 1px 0px
      padding: 1em !important
      cursor: pointer
      outline-color: $MAJOR-COLOR-2
      &:hover
        background-color: darken($LIGHT-COLOR-5, 5%)
      .-cohort-name
        .ui.header:first-child
          margin: -0.14285714em
        span
          font-size: 0.5em
        .button
          margin: 0em 0em 0em 0.8rem
          &:hover
            border-radius: 10em !important
          .menu
            transform: translateX(-80%)
          span
            font-size: 1rem
      .-addition
        max-height: 0px
        overflow: hidden
        padding: 0
        transition: max-height .4s
        .-details
          margin: 0 0.5rem
          ul
            margin-left: 1em
          li
            word-break: break-all
            color: #3b4252ba
          p
            margin-left: 1em
            color: #3b4252ba
    .item.selected
      background-color: $LIGHT-COLOR-2
      border-right: .5em $MAJOR-COLOR-1 solid
    .item.open .-addition
      max-height: 250px
      // overflow: auto
    .item:first-child
      border-top: $BORDER
  button.-load
    position: absolute
    bottom: 0
    right: 0
</style>
