import 'babel-polyfill' // for async/await

const variants = Array.from(new Array(100000), (v, i) => {
  return { id: i+1 }
})

export default {

  async getVariants(start, size, delay=1000) {
    await (() => new Promise(resolve => setTimeout(resolve, delay)))()
    return { rows: variants.slice(start, start + size), start }
  },

  variants,

  user: {
    avatar: 'http://i.pravatar.cc/32',
    cohorts: [
      { ctime: 1554352003000, name: 'Cohort 1' },
      { ctime: 1554357509000, name: 'Cohort 2' }
    ],
    configs: [
      { id: 1, lastModifiedTime: '2018-07-04T04:03:04.248Z', lastUsedTime: '2018-07-04T04:03:04.248Z', name: 'Config 1', filters: ['Quality Control', 'Gene Screening']},
      { id: 2, lastModifiedTime: '2018-07-04T04:03:04.248Z', lastUsedTime: '2018-07-04T04:03:04.248Z', name: 'Config 2', filters: ['Phenotype Screening', 'Gene Screening']},
      { id: 3, lastModifiedTime: '2018-07-04T04:03:04.248Z', lastUsedTime: '2018-07-04T04:03:04.248Z', name: 'Config 3', filters: ['Gene Screening']},
    ],
    sessions: [
      { id: 1, lastAccessedTime: '2018-07-04T04:03:04.248Z', name: 'Session 1', vcfs: ['1.vcf', '2.vcf'], filters: ['Quality Control', 'Gene Screening'] },
      { id: 2, lastAccessedTime: '2018-07-04T04:03:04.248Z', name: 'Session 2', vcfs: ['1.vcf', '3.vcf'], filters: ['Phenotype Screening', 'Gene Screening'] },
      { id: 3, lastAccessedTime: '2018-07-04T04:03:04.248Z', name: 'Session 3', vcfs: ['5.vcf'], filters: ['Gene Screening'] },
    ],
  },
  token: '',
  vcfid: '1',
  userName: 'User',
}
