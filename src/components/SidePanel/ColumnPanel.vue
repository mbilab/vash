<template lang="pug">
.-column-panel
  h3 Columns
  .-list
    .-block.ui.list(v-for='(columnGroup, name) in columnGroups' v-if='columnGroup.length')
      .itme.-block
        .-block-tittle(@click='toggleColumnGroup(columnGroup)')
          .-content {{ name.toUpperCase() }}
          i.check.square.outline.icon(v-if='isAllSelected(columnGroup)')
          i.square.outline.icon(v-else='isAllSelected(columnGroup)')
          .-full-text {{ name.toUpperCase() }}
        .list
          .item(v-for='column in columnGroup')
            .-block-item(@click='toggleColumn(column)')
              .-content {{ column }}
              i.check.square.outline.icon(v-if='isSelected(column)')
              i.square.outline.icon(v-else='isSelected(column)')
              .-full-text {{ column }}
      .ui.divider

</template>

<script>
import 'semantic-ui-offline/semantic.css'
import { mapState, mapGetters, mapMutations } from 'vuex'
export default {
  computed: {
    ...mapState(['columnGroups', 'filters']),
    ...mapGetters(['selectedColumns'])
  },
  data() {
    return {}
  },
  methods: {
    ...mapMutations(['selectFilterColumn']),

    isSelected(column) {
      return this.selectedColumns?.[column]?.selected
    },

    isAllSelected(columnGroup) {
      return columnGroup.every(this.isSelected)
    },

    toggleColumn(column, selected = null) {
      if (selected == null) selected = !this.isSelected(column)

      this.selectFilterColumn({ name: column, selected })
    },

    toggleColumnGroup(columnGroup) {
      if (this.isAllSelected(columnGroup)) {
        columnGroup.forEach(column => {
          this.toggleColumn(column, false)
        })
      } else {
        columnGroup.forEach(column => {
          this.toggleColumn(column, true)
        })
      }
    }
  }
}
</script>

<style lang="sass" scoped>
@import "~@/assets/variables.sass"
.-column-panel
  height: 100%
  min-width: $SIDE-PANEL-COMPONENT-WIDTH
  background-color: $LIGHT-COLOR-5
  border-right: $BORDER
  padding: 1em
  overflow: auto


.-list
  // padding: 1em
  .-block-tittle, .-block-item
    display: flex
    justify-content: space-between
    position: relative
    cursor: pointer
    .-content
      padding: 0em .5em
      max-width: 250px
      text-overflow: ellipsis
      overflow: hidden
    .-full-text
      padding: 0em .5em
      max-width: 250px
      pointer-events: none
      background-color: $LIGHT-COLOR-1
      position: absolute
      opacity: 0
    &:hover
      background-color: $LIGHT-COLOR-1
    &:hover > .-full-text
      max-width: none
      opacity: 1
      transition: opacity 0s .8s
    &:active > .-full-text
      opacity: 0
      transition: opacity 2s step-start
  .-block-item
    color: $MAJOR-COLOR-1

.list:last-child
  .ui.divider
    display: none

::-webkit-scrollbar-track
  background: rgba(0, 0, 0, 0)
  -webkit-box-shadow: none
</style>
