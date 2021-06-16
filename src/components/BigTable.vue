<template lang="pug">
.big-table
  .-table
    div(v-if='cohortInitialize')
      .-status
        p {{ cohort.n_variants }} variants
      .-status.-right
        a(v-if='knownSize',@click='scrollToTop') #[i.redo.icon]Refresh
    div(v-else)
      .-status
        p 0 variant
    .-thead(ref='theadFix')
      table.ui.celled.compact.striped.unstackable.table
        thead(v-if='knownSize || cohort.id'): tr
          th(v-for='column in fixedColumns') {{ column }}
    .-tbody.left(v-if='cohort.id',ref='tbodyFix',@scroll='scrollLeft')
      table.ui.celled.compact.striped.unstackable.table
        thead: tr
          th(v-for='column in fixedColumns',:class='colClass(column)') {{ column }}
        tbody
          tr(:style='paddingTop')
          tr(v-for='v in rendered.rows',:key='v["No."]')
            td(v-for='column in fixedColumns')
              a(v-if='isLocus(column, v[column])', @click='browseGenome(v[column])')
                | {{ v[column] }}
              span(v-else) {{ v[column] }}
          tr(:style='paddingBottom')
  .-table.right
    .-thead.right(ref='thead')
      table.ui.celled.compact.striped.unstackable.table
        thead: tr
          th(
            v-for='column in selectedColumns'
            :class='colClass(column)'
            @click='activateFilter(column.name)'
            )
            i.small.filter.icon(:class='{blue: isFiltered(column)}')
            | {{ column.name }}
    .-tbody.right(v-if='cohort.id',ref='tbody',@scroll='scrollRight')
      table.ui.celled.compact.striped.unstackable.table
        thead: tr
          th(v-for='column in selectedColumns',:class='colClass(column)')
            i.small.filter.icon
            | {{ column.name }}
        tbody
          tr(:style='paddingTop')
          tr(v-for='v in rendered.rows',:key='v["No."]')
            td(v-for='column in selectedColumns',:class='colClass(column)')
              a(v-if='isLocus(column.name, v[column.name])', @click='browseGenome(v[column.name])')
                | {{ v[column.name] }}
              span(v-else-if='v[column.name] == 0.000000000001 || v[column.dbName] == 0.000000000001') .
              span(v-else-if='v[column.name] == 0.000000000002 || v[column.dbName] == 0.000000000002') nan
              span(v-else) {{ v[column.dbName || column.name] }}
          tr(:style='paddingBottom')
    .-empty(v-else): .ui.small.compact.error.message Load a cohort to start

</template>

<script>
import 'babel-polyfill' // for async/await
import axios from 'axios'
import { debounce, throttle } from 'lodash'
import { mapActions, mapGetters, mapMutations, mapState } from 'vuex'

var createTree = require('functional-red-black-tree')

function Boundary() {
  this.min = Number.MIN_SAFE_INTEGER
  this.max = Number.MAX_SAFE_INTEGER
  this.find = function(tree, key) {
    var left = this.min,
      right = this.max

    if (!tree) return { left, right }
    let child = tree.root
    while (child) {
      if (child.key == key) {
        return { left: child.key, right: child.key }
      }

      if (child.key >= key) {
        right = child.key
        child = child.left
      } else {
        left = child.key
        child = child.right
      }
    }
    return { left, right }
  }
}

export default {
  computed: {
    ...mapGetters(['cohort', 'selectedColumns', 'sampleBamFiles']),
    ...mapState(['filters']),

    cohortInitialize() {
      if (this.cohort.n_variants) {
        if (
          JSON.stringify(this.samples) !=
          JSON.stringify(this.cohort.samples.split(','))
        ) {
          let samples = this.samples
          this.setCohortSamples({ samples })
          this.samples = this.cohort.samples.split(',')
          this.info = JSON.parse(this.cohort.info)
          this.info['bam'] = this.info['bam'].split(',')
        }

        return this.cohort.n_variants
      }
      if (!this.loaded.rows.length) return 0
    },

    knownSize() {
      if (this.cohort.n_variants) return this.cohort.n_variants
      if (!this.loaded.rows.length) return 0
      return this.loaded.start + this.loaded.rows.length + this.visibleBuffer
    },

    paddingBottom() {
      const e = this.rendered.start + this.rendered.rows.length
      // chrome is broken at ~493000 row (row hight = 34)
      // safari is broken at 33554400 px
      const size = Math.min(this.knownSize, 400000) - e
      const height = Math.max(size, 0) * this.rowHeight + 'px'
      return { height }
    },

    paddingTop() {
      const height = this.rendered.start * this.rowHeight + 'px'
      return { height }
    }
  },

  data() {
    return {
      info: {},
      fixedColumns: ['No.'],
      loaded: {
        start: 0,
        rows: []
      },
      db_index: {},
      tree: createTree(), // not reactive
      lock: 0,
      rendered: {
        start: 0,
        rows: []
      },
      rowHeight: 34,
      redirect: '',
      samples: [],
      boundary: new Boundary(),
      nCountingVariants: 0,
      timer: null,
      match_counts: {} // not reactive
    }
  },

  methods: {
    ...mapActions(['activateFilter', 'getVariants', 'setCacheItem']),
    ...mapMutations(['setCohortSamples']),

    getSamples(v) {
      return Object.values(JSON.parse(v))
    },

    colClass: col => ({
      '-filterable': col.filterable,
      '-numeric': col.numeric
    }),

    fitColumn: debounce(function() {
      // {{{
      if (!this.rendered.rows.length) return
      const theadThs = this.$refs.thead.querySelectorAll('th')
      const tbodyThs = this.$refs.tbody.querySelectorAll('th')
      const theadFix = this.$refs.theadFix.querySelectorAll('th')
      const tbodyFix = this.$refs.tbodyFix.querySelectorAll('th')
      if (theadThs.length != tbodyThs.length) return //! something wrong
      for (let i = 0; i < theadThs.length; ++i)
        theadThs[i].style.minWidth = tbodyThs[i].offsetWidth + 'px'
      for (let i = 0; i < theadFix.length; ++i)
        theadFix[i].style.minWidth = tbodyFix[i].offsetWidth + 'px'
    }, 0), // }}}

    isFiltered(col) {
      return (
        col.name && this.filters[col.name] && this.filters[col.name].filtered
      )
    },

    in(query, range) {
      // <-----------range------------->
      //               ^
      //             query
      const rangeEnd =
        range.start + range.rows.length <= this.cohort.n_variants ||
        !this.cohort.n_variants
          ? range.start + range.rows.length
          : this.cohort.n_variants
      return query >= range.start && query <= rangeEnd
    },

    isLocus: (columnName, value) =>
      ('MostImportantFeatureGene' == columnName || 'POS' == columnName) &&
      '.' != value,

    async browseGenome(locus) {
      this.info = JSON.parse(this.cohort.info)
      this.info['bam'] = this.info['bam'].split(',')

      if (this.cohort.samples.length) {
        let selectedSamples = []
        for (let key in this.selectedColumns) {
          if (this.selectedColumns[key].group == 'samples')
            selectedSamples.push(key)
        }

        let sampleWithoutBam = []
        for (let sample of selectedSamples) {
          if (this.sampleBamFiles[sample] == null) {
            sampleWithoutBam.push(sample)
          }
        }

        if (
          !sampleWithoutBam.length ||
          window.confirm(
            `Following sampleIDs has no BAMfile filename including sampleID:\n    ${sampleWithoutBam.join(
              ',\n    '
            )}\nShow other selected samples in IGV?`
          )
        ) {
          for (let sample of selectedSamples) {
            if (sampleWithoutBam.includes(sample)) continue
            axios
              .get(
                'http://localhost:60151/load?file=' +
                  this.sampleBamFiles[sample] +
                  '&locus=' +
                  locus +
                  '&genome=hg19'
              )
              .catch(err => console.log(err))
          }
        }
      } else {
        let numBams = this.info.bam.length
        if (numBams > 1) {
          if (
            window.confirm(
              `Do you want to show all ${numBams} BAM files in IGV?`
            )
          ) {
            for (var i = 0; i < this.info.bam.length; i++) {
              axios
                .get(
                  'http://localhost:60151/load?file=' +
                    this.info.bam[i] +
                    '&locus=' +
                    locus +
                    '&genome=hg19'
                )
                .catch(err => console.log(err))
            }
          }
        }
      }
    },

    async load(start = 0) {
      // load {{{
      let size =
        start + this.loadSize <= this.cohort.n_variants ||
        !this.cohort.n_variants
          ? this.loadSize
          : this.cohort.n_variants - start
      let { left, right } = this.boundary.find(this.tree, start)

      let idQuery, tableStartId
      let reverse = false
      if (this.db_index[start]) {
        idQuery = { ['id__gte']: this.db_index[start] }
        tableStartId = 0
      } else if (
        start - left > right - start - size &&
        right != this.boundary.max
      ) {
        // left ----------------------------right
        //                ^  <---------->
        //              start     size
        idQuery = { ['id__lt']: this.db_index[right] }
        tableStartId = right - start - size
        reverse = true
      } else if (left != this.boundary.min) {
        idQuery = { ['id__gte']: this.db_index[left] }
        tableStartId = start - left
      } else {
        tableStartId = start
      }
      const [data, error] = await this.getVariants({
        start: tableStartId,
        size,
        id_query: idQuery,
        reverse,
        match_counts: this.match_counts
      })
      if (error) {
        this.lock = 0
        throw error
      }
      if (data.rows.length == 0) {
        this.lock = 0
        return
      }
      this.match_counts = data.match_counts

        // add No. column
        let no = start
        for (const v of data.rows) v['No.'] = ++no

        const save_db_index = (id, db_index) => {
          this.$set(this.db_index, id, db_index)

          this.tree = this.tree.insert(id, '')

          let key = `/cohort/${this.cohort.id}/` + this.cohort.queries
          let value = {
            ...this.cohort,
            db_index: JSON.stringify(this.db_index)
          }
          this.setCacheItem({ key, value })
        }

        // save db_end_id and db_start_id in vue.dat, tree, and cache
        if (!this.db_index[start + data.rows.length]) {
          save_db_index(start + data.rows.length, data.db_end_id + 1)
        }
        if (!this.db_index[start]) {
          save_db_index(start, data.db_start_id)
        }

        // update loaded range
        const end =
          start + data.rows.length <= this.cohort.n_variants
            ? start + data.rows.length
            : this.cohort.n_variants
        const loaded = this.loaded
        if (this.in(start, loaded)) {
          // start in between loaded range, concat
          loaded.rows.splice(
            start - loaded.start,
            data.rows.length,
            ...data.rows
          )
        } else if (this.in(end, this.loaded)) {
          // end in between loaded range, concat
          loaded.rows.splice(0, end - loaded.start, ...data.rows)
          this.loaded.start = start
        } else {
          // no overlap, new loaded range
          loaded.rows = []
          loaded.rows.splice(0, data.rows.length, ...data.rows)
          loaded.start = start
        }
        this.lock = 0
        if (this.rendered.start - this.loaded.start > this.loadSize)
          this.onScroll()
        return resolve()
      })
    }, // }}}

    scrollLeft() {
      this.$refs.tbody.scrollTop = this.$refs.tbodyFix.scrollTop
      this.onScroll()
    },

    scrollRight() {
      this.$refs.tbodyFix.scrollTop = this.$refs.tbody.scrollTop
      this.onScroll()
    },

    scrollToTop() {
      this.$refs.tbody.scrollTop = 0
      this.$refs.tbodyFix.scrollTop = 0
      this.onScroll()
    },

    onScroll: throttle(async function() {
      // {{{
      this.render()
      this.$refs.thead.scrollLeft = this.$refs.tbody.scrollLeft

      // calculate buffered visible range, `bvr`
      const vr = this.visibleRange()
      const bvr = {
        start: Math.max(vr.start - this.visibleBuffer, 0),
        end: Math.min(vr.end + this.visibleBuffer, this.knownSize)
      }

      // check whether `bvr` has been loaded
      const loadAbove = !this.in(bvr.start, this.loaded)
      const loadBelow =
        !this.in(bvr.end, this.loaded) ||
        (this.loaded.start == 0 && this.loaded.rows.length == 0)
      let start = 0
      if (loadAbove && loadBelow)
        start = Math.max(Math.round(vr.mid - this.loadSize / 2), 0)
      else if (loadAbove) start = this.loaded.start - this.loadSize
      else if (loadBelow) start = this.loaded.start + this.loaded.rows.length
      else return
      if (this.lock == 0) {
        this.lock = 1
        start = Math.round(start / this.loadSize) * this.loadSize
        await this.load(start)
        // render
        this.render()
      }
    }, 200),

    // if not tell, assume all row are loaded
    async render() {
      // {{{
      // get visible range, `vr`
      const vr = this.visibleRange()

      // // if visible range has not loaded, load again
      let loadedStart = this.loaded.start
      let loadedEnd = this.loaded.start + this.loaded.rows.length
      if (vr.start < loadedStart) {
        let start = vr.start - (vr.start % this.loadSize)
        if (this.lock == 0) {
          this.lock = 1
          await this.load(start)
          this.lock = 0
        }
      }
      if (loadedEnd < vr.end && loadedEnd < this.knownSize) {
        let start = vr.end - (vr.end % this.loadSize)
        if (this.lock == 0) {
          this.lock = 1
          await this.load(start)
          this.lock = 0
        }
      }

      // if `vr` has been rendered, skip render
      if (this.in(vr.start, this.rendered) && this.in(vr.end, this.rendered))
        return

      // calculate render range
      const start = Math.max(
          this.loaded.start,
          Math.floor(vr.mid - this.renderedMax / 2)
        ),
        end = Math.min(
          this.loaded.start + this.loaded.rows.length,
          Math.ceil(vr.mid + this.renderedMax / 2)
        )

      // render
      this.rendered.rows = this.loaded.rows.slice(
        start - this.loaded.start,
        end - this.loaded.start
      )
      this.rendered.start = start

      // adjust column widths
      this.fitColumn()
    }, // }}}

    async reset() {
      this.db_index = {}
      this.tree = createTree()
      clearInterval(this.timer)
      this.timer = null
      this.nCountingVariants = 0
      this.loaded.rows.splice(0, this.loaded.rows.length)
      this.rendered.rows.splice(0, this.rendered.rows.length)

      // after cohort.id set and tbody in dom created
      this.$nextTick(() => {
        if (this.$refs.tbody) {
          this.scrollToTop()
        }
      })
    },

    // visible range {{{
    visibleRange() {
      const el = this.$refs.tbody
      let height = 0,
        top = 0
      if (el) (height = el.offsetHeight), (top = el.scrollTop)
      const start = Math.floor(top / this.rowHeight)
      const end = Math.ceil((top + height) / this.rowHeight)
      return { start, end, mid: Math.round((start + end) / 2) }
    } // }}}
  },

  mounted() {
    this.reset()
    this.$root.$on('BigTable:reset', this.reset)
  },

  props: {
    // depend on memory
    loadedMax: { default: 1000 },

    // see `visibleBuffer`
    loadSize: { default: 100 },

    // depend on memory, make sure this ≤ `loadedMax`
    renderedMax: { default: 50 },

    // visible range (VR): rows actually visible
    //  * VR is usually < 50 rows
    //  * suppose screen height ≤ 1000 px
    //  * suppose row height ≥ 20 px
    //  * visible range < 1000 / 20 = 50
    // buffered visible range (BVR): VR ± `visibleBuffer`
    //  * make sure `loadSize` > BVR
    //  * ideally, BVR should be pre-loaded
    //  * thus, load request is emitted when BVR exceeds loaded range
    //  * 2 load requests for 1 BVR is not reasonable
    // e.g. set `visibleBuffer` to 2 * VR
    //  * rows upward/downward 2 * VR, BVR ≈ 5 * VR, are pre-loaded
    //  * `visibleBuffer` = 100, `loadSize` ≥ 250
    visibleBuffer: { default: 40 }
  },

  watch: {
    filters: {
      deep: true,
      handler() {
        this.fitColumn()
      }
    }
  }
}
</script>

<style lang="sass" scoped>
.big-table
  flex: 1 1 auto
  padding: 1em
  display: flex
  flex-direction: row
  overflow: hidden
  max-height: 1200px

.-status
  position: absolute
.-right
  right: 1em
  cursor: pointer

.-table
  display: flex
  flex-direction: column
  overflow: hidden
  flex: 1 0 60px

.-table.right
  flex: 1 1 auto
  position: relative

.-thead.right
  position: relative
  margin-right: 10px // for scroll bar
  overflow: hidden

  table
    border-bottom: 0
    border-bottom-left-radius: 0
    border-bottom-right-radius: 0

    th
      border-bottom: 0

.-thead
  flex: 0 0 auto
  position: relative
  margin-top: 20px

.-tbody
  flex: 1 1 auto
  overflow: auto

  table
    border-top: 0
    border-top-left-radius: 0
    border-top-right-radius: 0

  thead th
    line-height: 0
    padding-bottom: 0
    padding-top: 0
    visibility: hidden

    .icon
      line-height: 0

.-tbody.left::-webkit-scrollbar
  width: 0px

.-tbody.right
  overflow: auto

.ui.table
  margin: 0

  th, td
    white-space: nowrap

    &.-numeric
      text-align: right

  th
    border-bottom: 0
    &.-filterable
      cursor: pointer

      .icon
        display: inline

    .icon
      display: none

.-empty
  border: 1px solid rgba(34, 36, 38, 0.15)
  border-bottom-left-radius: 0.28571429rem
  border-bottom-right-radius: 0.28571429rem
  text-align: center

  .ui.message
    margin-top: 1em
</style>
// }}}
