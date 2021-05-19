<template lang="pug">
.ui.search.multiple.selection.dropdown(
  :class='{ active: menuDropped }'
  ref='root'
  )
  i.search.icon(v-show='!value.length')
  i.dropdown.icon(@click.stop='menuDropped = !menuDropped')
  a.ui.label(v-for='v in value') {{ v }}#[i.delete.icon(@click.stop='delTerm(v)')]
  input.search(
    v-model.trim='input'
    @input='setTerms(input)'
    @keydown.backspace='backspace'
    @keyup.enter='addTerm(input)'
    ref='input'
    :style='{ minWidth: 1.1 * input.length + "em" }'
    type='text'
    )
  .menu(v-if='activeColumnName!="POS"')
    .message(v-if='!terms.length') No matches found.
    .item(v-else,v-for='v in terms',@click.stop='addTerm(v)') {{ v }}
  .menu(v-if='activeColumnName=="POS"')
    .message e.g. chrM:35-35
</template>

<script>
import { mapState, mapActions } from 'vuex'
export default {
  beforeDestroy() {
    document.removeEventListener('click', this.click)
  },

  computed: {
    ...mapState(['columns'])
  },

  created() {
    document.addEventListener('click', this.click)
    this.setTerms(this.input)
  },

  data: () => ({
    menuDropped: false,
    input: '',
    terms: []
  }),

  methods: {
    ...mapActions(['getTerms']),
    addTerm(v) {
      if (!v || this.value.includes(v)) return
      this.value.push(v)
      this.input = ''
    },

    backspace() {
      if (this.input) return
      const n = this.value.length
      if (n) this.delTerm(this.value[n - 1])
    },

    click(e) {
      const el = this.$refs.root
      this.menuDropped = el == e.target || el.contains(e.target)
      if (this.menuDropped) this.$refs.input.focus()
    },

    delTerm(v) {
      const i = this.value.indexOf(v)
      if (-1 != i) this.value.splice(i, 1)
    },

    async setTerms(input) {
      if (this.activeColumnName == 'POS') return
      let terms = await this.getTerms({
        dbName:
          this.columns[this.activeColumnName].dbName ||
          this.columns[this.activeColumnName].name,
        keyword: input
      })
      this.$set(this, 'terms', terms)
    }
  },

  props: {
    activeColumnName: String,
    size: { default: 500 },
    value: { default: [] }
  },
  watch: {
    activeColumnName: function(value) {
      this.setTerms(this.input)
    }
  }
}
</script>

<style lang="sass" scoped>
@import "~@/assets/variables.sass"

.ui.active.dropdown .menu
  display: block
.ui.selection.dropdown
  display: block
  border-radius: .5em
  border: solid 1px $LIGHT-COLOR-1
  .icon+input.search
    padding-left: 2em
  .menu
    border: solid 1px $LIGHT-COLOR-1
.ui.selection.dropdown:last-child
  margin-bottom: 0
.ui.selection.dropdown > .search.icon
  width: 1.18em
  left: 1em
  top: .6em
</style>
