<template lang="pug">
.-cohort-creator
  .-title.-flex-container
    h3 Create a Cohort
    i.large.close.icon(@click="$emit('changeComponent', 'cohort-list')")
  .ui.form
    .field
      label Cohort Name
      input(type="text",v-model='cohortName')
    .field
      label Description
      textarea(type="text",v-model='description')
    .field
      label Show all samples
      .field.ui.toggle.checkbox
        input(type="checkbox", v-model='allSamples')
        label.checkbox build cohort with all samples in vcf file
    .field
      label VCF File
      span Select a vcf file
      .ui.selection.list
        .item(v-for="(vcf, idx) in user.vcfs" :class="{ active: selectedVCFIdx == idx }" @click="selectVCF(idx)")
          i.file.outline.icon
          .content
            .header {{ vcf.path }}
    .field
      label Edit Bam Files
      textarea(v-model="newBams",placeholder="Add URL of bam file1, URL of bam file2, URL of bam file3, … ",@input="parseBams")
    .field
      .-list
        .-item.-flex-container(v-if="bams!=''",v-for="(bam, idx) in bams")
          p {{ bam }}
          i.close.icon(@click="deleteBams(idx)")
    button.fluid.ui.button(@click='create') Create new cohort
  // .-button
</template>

<script>
import 'semantic-ui-offline/semantic.css'
import { mapState, mapActions } from 'vuex'
export default {
  mounted() {
    this.reset()
  },

  data() {
    return {
      allSamples: false,
      selectedVCFIdx: null,
      cohortName: '',
      description: '',
      files: {},
      newBams: '',
      bams: []
    }
  },
  computed: {
    ...mapState(['user'])
  },
  methods: {
    ...mapActions(['createCohort']),

    selectVCF(idx) {
      let selectedFileName = this.user.vcfs[this.selectedVCFIdx]?.path
      if (this.files?.[selectedFileName]) {
        this.files[selectedFileName].selected = false
      }

      if (this.selectedVCFIdx == idx) {
        this.selectedVCFIdx = null
      } else {
        this.selectedVCFIdx = idx
        selectedFileName = this.user.vcfs[this.selectedVCFIdx].path
        this.files[selectedFileName].selected = true
      }
    },

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

    create() {
      if (this.selectedVCFIdx == null) {
        alert('selecte vcf file, before you create a cohort.')
        return
      }
      // if ('local' == this.type) {
      //   let bams = this.user.bams.filter(bam => this.selectedBam(bam))
      //   for (let i in bams) {
      //     this.bam += 'http://localhost:10105/' + bams[i].path
      //     if (i != bams.length - 1) {
      //       this.bam += ','
      //     }
      //   }
      // } else {
      //   for (let i in this.webBams) {
      //     this.bam += this.webBams[i].path
      //     if (i != this.webBams.length - 1) {
      //       this.bam += ','
      //     }
      //   }
      // }
      this.createCohort({
        cohort: this.files,
        name: this.cohortName,
        description: this.description,
        bam: this.bams.join(','),
        allSamples: this.allSamples
      }).then(() => {
        this.$root.$emit('CohortList:update')
      })
      this.reset()
      this.$emit('changeComponent', 'cohort-list')
    },

    reset() {
      this.cohortName = ''
      this.files = {}
      this.selectedVCFIdx = null
      for (const v of this.user.vcfs)
        this.$set(this.files, v.path, {
          case: false,
          control: false,
          path: v.path,
          selected: false
        })
      // for (const v of this.user.bams)
      //   this.$set(this.localBams, v.sample, { path: v.path, selected: false })
    }
  }
}
</script>

<style lang="sass" scoped>
@import "~@/assets/variables.sass"

.-cohort-creator
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
    display: flex
    justify-content: space-between
    align-items: center
  .-title
    padding: 1em
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
    .checkbox
      margin-bottom: 0.4em
    input, textarea
      border-radius: .5em
    .field
      margin-bottom: 1.5em
    .field label:not(.checkbox)
      font-size: 1.1em
    // .field.checkbox label
    //   font-size: .92em
  .list
    margin: 0
    padding-right: 1em
    border: $BORDER
    border-radius: .5em
    .item
      padding: 0.2em 1em 0.2em 0.2em
      .header
        color: rgba(0,0,0,0.4)
        transition: color 0.3s ease
        word-break: break-all
      .description
        font-size: 0.8em
      &:hover
        .header
          color: rgba(0,0,0,0.87)
    .item.active
      background-color: rgba(0,0,0,0.12)
      .header
        color: rgba(0,0,0,0.87)
      &:hover
        background-color: rgba(0,0,0,0.12)
  .-button
    padding: 1em
  ::-webkit-scrollbar
    width: 6px
  ::-webkit-scrollbar-track
    border-radius: 6px
</style>
