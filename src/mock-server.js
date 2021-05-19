import { createServer } from 'miragejs'
let responses = require('./responses')

export const runMockingServer = () =>
  createServer({
    routes() {
      this.post('/login', () => ({
        ok: true,
        token: 'abc123'
      }))

      this.get('/users', () => ({
        ok: true,
        data: {
          username: 'mirage mock!'
        }
      }))

      this.post('/variants/*', () => responses.variants)

      this.post('/me', () => responses.me)

      this.post('/cohort/:id', (schema, request) => {
        let id = request.params.id
        if (id == 1) return responses.cohort_query // query = "QUAL_gt: 100"
      })

      this.post('/terms/:id', (schema, request) => {
        let id = request.params.id
        if (id == 1) return responses.terms['1']
        if (id == 5) return responses.terms['5']
      })
    }
  })
