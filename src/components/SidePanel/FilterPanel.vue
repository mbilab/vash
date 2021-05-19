<template lang="pug">
.-filter-panel
  h3 Filter
    .ui.checkbox
      input(type='checkbox',v-model='allColumnsShown')
      label Show all columns

  .-filter-menu(v-for='(filterName, idx) in stagedFilters')
    .-menu-head.flex-end(v-if='!filterName.includes("reset")')
      .button(tabindex=0 :class='{add: filterName.includes("Add")}') {{ filterName }}
        i.dropdown.icon
      ul
        li(
          v-for='( columnGroup, name ) in columnGroups',
          v-if='columnGroup.length'
        )
          span {{ name.toUpperCase() }}
          ul
            li(
              v-if='isShown(column)'
              v-for='column in columnGroup'
              @mousedown='setStagedFilters({idx:idx, column:column})'
              :class='{disabled: stagedFilters.includes(column)}'
            ) {{ column }}
      i.close.icon(v-if='!filterName.includes(" ")' @click='resetStagedFilter({idx, filterList})' )
    .-menu-head(v-if="filterName.includes('reset')")
      p {{ filterName }}

    .-filter-value(v-if='filters[filterName]')
      .-contain(v-if='"position" in filters[filterName]')
        combo-input.fluid(v-model='filters[filterName].position',:activeColumnName='filterName')
      .-contain(v-if='"contain" in filters[filterName]')
        // h5 Search:
        combo-input.fluid(v-model='filters[filterName].contain',:activeColumnName='filterName')
      .-equality(v-if='"equality" in filters[filterName]')
        .fluid.ui.buttons
          .ui.button(
            v-for='v in ["?", "<", "≤", "=", "≥", ">"]'
            @click='filters[filterName].equality = v'
            :class='{ active: v == filters[filterName].equality }'
            ) {{ v }}
        .fluid.ui.input(:class='{ disabled: "?" == filters[filterName].equality }')
          input(v-model.number='filters[filterName].threshold',type='number')
      .-equalTo(v-if='"equalTo" in filters[filterName]')
        h5 Equal to:
        .ui.checkbox(v-for='equalTo in filters[filterName].equalTo')
          input(checked='checked',type='checkbox', v-model='equalTo[Object.keys(equalTo)[0]]')
          label {{ Object.keys(equalTo)[0] || filters[filterName].equalToEmpty}}

  .fluid.ui.-apply.button( @click='apply', :class='{ "major-button": applyButtonActivated }') Apply

  h4(v-if='filtered.length') Filtered:
    .-filter-list
      ul.ui.middle.aligned.-non-selection.list
        .item(v-for="detail in filtered")
          .middle.aligned.content {{ detail }}
  h4(v-if='filterList.length') Filtered:
    .-filter-list
      ul.ui.middle.aligned.selection.list
        .item(v-for="filter in filterList", @click='activateFilter(filter.name)')
          .right.floated.content(@click.stop='clearFilter(filter.name)')
            i.close.icon
          .middle.aligned.content(:class='{ delete: filter.delete }') {{ filter.detail }}


</template>

<script>
import 'semantic-ui-offline/semantic.css'
import { mapActions, mapMutations, mapState, mapGetters } from 'vuex'
export default {
  components: {
    'combo-input': require('../ComboInput.vue').default
  },

  computed: {
    ...mapGetters(['cohort', 'filtered', 'filterDetails']),
    ...mapState([
      'columnGroups',
      'filters',
      'columns',
      'selectedCohortIdx',
      'stagedFilters'
    ])
  },

  data() {
    return {
      allColumnsShown: false,
      applyButtonActivated: false,
      filterList: []
    }
  },

  methods: {
    ...mapActions(['getCohort', 'setCacheItem', 'activateFilter']),
    ...mapMutations([
      'resetFilter',
      'resetStagedFilter',
      'resetStagedFilters',
      'setCohortFilters',
      'setCohortNVariants',
      'setStagedFilters'
    ]),

    async apply() {
      this.applyButtonActivated = false
      this.setCacheItem({ key: 'filters', value: this.filters })

      let queries = []
      for (const k in this.filters) {
        const filter = this.filters[k]
        const queriesLen = queries.length

        if (filter.contain) {
          const values = filter.contain
          if (values.length) {
            if (this.columns[k]['dbName']) {
              queries.push({
                [this.columns[k]['dbName'] + '__match']: values
              })
            } else if ('ID' != k) {
              queries.push({ [k + '__match']: values })
            } else if ('ID' == k) {
              queries.push({ ['variantID__match']: values })
            }
          }
        }

        if ('<' == filter.equality)
          queries.push({
            [k + '__lt']: filter.threshold,
            [k + '__gt']: 0.000000000001
          })
        else if ('≤' == filter.equality)
          queries.push({
            [k + '__lte']: filter.threshold,
            [k + '__gt']: 0.000000000001
          })
        else if ('=' == filter.equality) queries.push({ [k]: filter.threshold })
        else if ('≥' == filter.equality)
          queries.push({ [k + '__gte']: filter.threshold })
        else if ('>' == filter.equality)
          queries.push({ [k + '__gt']: filter.threshold })

        if (filter.equalTo) {
          const values = filter.equalTo
            .filter(v => v[Object.keys(v)[0]])
            .map(v => Object.keys(v)[0])
          if (values.length && values.length < filter.equalTo.length)
            queries.push({ [k + '__match']: values })
        }

        if (filter.position) {
          const values = filter.position
          if (values.length) {
            queries.push({
              position: values
            })
          }
        }

        this.$set(this.filters[k], 'filtered', queries.length > queriesLen)
        this.filterList = this.filterDetails
      }

      queries = JSON.stringify(queries)
      if (queries == this.cohort.queries) return

      this.setCohortFilters({ queries })

      this.$root.$emit('BigTable:reset')
      this.resetStagedFilters()

      var count = 1
      let timer = setInterval(() => {
        this.setCohortNVariants({
          idx: this.selectedCohortIdx,
          nVariants: ++count * 100 + '+'
        })
      }, 1500)
      let queryed_cohort = await this.getCohort({
        id: this.cohort.id,
        queries
      })
      clearInterval(timer)
      this.setCohortNVariants({
        idx: this.selectedCohortIdx,
        nVariants: queryed_cohort.n_variants
      })
    },

    clearFilter(column) {
      this.applyButtonActivated = true
      this.resetFilter(column)
      this.filterList = this.filterDetails
    },

    isShown(column) {
      if (this.allColumnsShown) return this.columns[column].filterable
      return this.columns[column].filterable && this.columns[column].selected
    }
  },
  watch: {
    stagedFilters: {
      handler: function(val, oldVal) {
        this.applyButtonActivated = val.length > 1
      },
      deep: true
    }
  }
}
</script>

<style lang="sass" scoped>
@import "~@/assets/variables.sass"

.delete
  text-decoration: line-through

.-filter-panel
  padding: 1em
  height: 100%
  width: $SIDE-PANEL-COMPONENT-WIDTH
  background-color: $LIGHT-COLOR-5
  border-right: $BORDER
  overflow-y: scroll

h3
  .checkbox
    float: right

.-apply
  color: $DARK-COLOR-4
  box-shadow: rgba(184, 194, 215, 0.35) 0px 3px 1px 0px

.major-button
  background-color: $DARK-COLOR-2
  color: $LIGHT-COLOR-3

.major-button:hover
  background-color: $DARK-COLOR-1
  color: $LIGHT-COLOR-2

.-filter-menu
  padding: 1em
  margin: .5em 0em
  position: relative
  background-color: $LIGHT-COLOR-5
  border-radius: .5em
  border: $BORDER
  box-shadow: rgba(184, 194, 215, 0.35) 0px 3px 6px 0px
  .-menu-head
    display: flex
    justify-content: space-between
    align-items: center
    >.button
      // min-width: 10em
      display: inline-block
      color: $DARK-COLOR-3
      background-color: $LIGHT-COLOR-5
      // border: solid 1px $LIGHT-COLOR-1
      border-radius: .5em
      outline-color: $MAJOR-COLOR-2
      font-size: 1.1em
      .dropdown.icon
        margin: 0 .5em
        float: right
    >.button:hover
      cursor: pointer
      color: $DARK-COLOR-1
      // border: solid 1px rgba(0,0,0,0.3)
    > ul
      align-self: flex-start
      border-radius: .5em
      border: solid 1px $LIGHT-COLOR-1
      box-shadow: rgba(184, 194, 215, 0.35) 0px 3px 6px 0px
      width: calc(#{$SIDE-PANEL-COMPONENT-WIDTH} - 4em)
      max-height: 30em
      overflow: auto
      z-index: 10
      background-color: $LIGHT-COLOR-5
      position: absolute
      left: -1px
      transition: opacity 0.4s ease,transform 0.4s ease
      transform: translateY(-1em)
      opacity: 0
      /* opacity: 1 */
      pointer-events: none
      /* pointer-events: none */
      > li:first-child
        padding-top: .3em
      li
        list-style: none
        span
          padding: 0em 1em
        > ul
          color: $MAJOR-COLOR-1
          li
            padding: .5em 2em
          li:hover
            background-color: $LIGHT-COLOR-1
          .disabled
            opacity:  .3
    >.button:focus + ul
      opacity: 1
      transform: translateY(2em)
      pointer-events: all
      li
        cursor: pointer
    >.button.add
      border: none
      // flex: 1 auto
    i.close
      align-self: flex-start

.-filter-value
  margin: 1em 0 0 0
  .fluid
    margin: 1em 0em
  .fluid:last-child
    margin-bottom: 0

.-equality
  .ui.button
    padding: 0.78571429em
.-equalTo
  > .ui.checkbox
    display: inline
h4
  margin: .5em 1em

.-filter-list
  .-non-selection > .item
    background: transparent
    padding: 0.5em 0.5em
    margin: 0em
    color: rgba(0, 0, 0, 0.4)
    border-radius: 0.5em
  .list
    li
      position: static
    .item:hover
      cursor: auto
    .close:hover
      cursor: pointer


::-webkit-scrollbar-track
  background: rgba(0, 0, 0, 0)
  -webkit-box-shadow: none
</style>
