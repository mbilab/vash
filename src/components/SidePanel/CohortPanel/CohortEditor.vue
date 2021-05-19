<template lang="pug">
.-bam-editor
  .-title.-flex-container
    h3 Edit Cohort
    i.large.close.icon(@click="$emit('changeComponent', 'cohort-list')")
  .ui.form
    .field
      label Cohort Name
      input(type="text",v-model='cohortName')
    .field
      label Description
      textarea(type="text",v-model='description')
    .field
      label Edit Bam Files
      textarea(v-model="newBams", placeholder="Add URL of bam file1, URL of bam file2, URL of bam file3, … ", @input="parseBams")
      .-list
        .-item.-flex-container(v-if="bams!=''",v-for="(bam, idx) in bams")
          p {{ bam }}
          i.close.icon(@click="deleteBams(idx)")
    button.fluid.ui.button(@click='save') Save
</template>

<script>
import 'semantic-ui-offline/semantic.css'
import { mapGetters, mapActions, mapState } from 'vuex'

export default {
  activated() {
    this.bams = this.info.bam.split(',').filter(v => v)
    this.newBams = this.bams.join(',\n')
    this.$set(this, 'bams', this.bams)

    this.description = this.info.description.detail
    this.cohortName = this.info.description.title
  },

  computed: {
    ...mapGetters(['getInfoById']),
    info: {
      get() {
        return this.getInfoById(this.cohortIdx)
      },
      set(value) {
        this.updateUserCohort({
          idx: this.cohortIdx,
          update_obj: { info: JSON.stringify(value) }
        })
      }
    }
  },

  data() {
    return {
      description: '',
      cohortName: '',
      newBams: '',
      bams: []
    }
  },

  props: ['cohortIdx'],

  methods: {
    ...mapActions(['updateUserCohort']),
    parseBams(event) {
      let newBams = this.newBams

      while (newBams[newBams.length - 1] == ',') {
        newBams = newBams.slice(0, newBams.length - 1)
      }
      while (newBams[0] == ',') {
        newBams = newBams.slice(1)
      }
      if (!newBams) return

      newBams
        .split(',')
        .map(v => v.trim())
        .filter(v => v)
        .forEach((v, i) => this.$set(this.bams, i, v))
    },

    deleteBams(bam_idx) {
      this.bams.splice(bam_idx, 1)
    },

    save() {
      this.info = {
        ...this.info,
        bam: this.bams.join(','),
        description: {
          detail: this.description,
          title: this.cohortName
        }
      }
      this.updateUserCohort({
        idx: this.cohortIdx,
        update_obj: { name: this.cohortName }
      })
    }
  }
}
</script>

<style lang="sass" scoped>
@import "~@/assets/variables.sass"

.-bam-editor
  position: absolute
  top: 0
  left: 0
  margin-left: $COHORT-PANEL-COMPONENT-MARGIN-X
  margin-right: $COHORT-PANEL-COMPONENT-MARGIN-X
  margin-top: $COHORT-PANEL-COMPONENT-MARGIN-TOP
  margin-bottom: $COHORT-PANEL-COMPONENT-MARGIN-BOTTOM
  height: calc(100% - #{2 * $COHORT-PANEL-COMPONENT-MARGIN-TOP})
  width: calc(100% - #{2 * $COHORT-PANEL-COMPONENT-MARGIN-X})

  background-color: $LIGHT-COLOR-5
  border: $BORDER
  border-radius: .5em
  box-shadow: rgba(184, 194, 215, 0.35) 0px 3px 1px 0px
  display: flex
  flex-direction: column
  .-flex-container
    padding: 1em
    display: flex
    justify-content: space-between
    align-items: center
  .-title
    h3
      margin: 0
    .icon
      margin: 0
      cursor: pointer
  .form
    overflow: auto
    padding: 1em
    textarea
      height: 6em
    input, textarea
      border-radius: .5em
  button
    margin-bottom: 1em
  .-list
    overflow: auto
    .-item
      padding: 0.3em 1em
      p
        text-overflow: ellipsis
        white-space: nowrap
        overflow: hidden
        flex: 1
        margin: 0
      .icon
        margin: 0 0 0.3em 2em
        cursor: pointer
  ::-webkit-scrollbar
    width: 0.6em
  ::-webkit-scrollbar-track
    border-radius: 5px
</style>
