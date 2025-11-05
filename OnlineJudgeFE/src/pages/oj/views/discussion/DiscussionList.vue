<template>
  <div class="flex-container">
    <div id="main">
      <Panel shadow>
        <div slot="title">Discussions</div>
        <div slot="extra">
          <Button size="small" icon="refresh" @click="fetch" :loading="loading">Refresh</Button>
        </div>
        <Table :columns="columns" :data="rows" :loading="loading" no-data-text="No discussions yet"></Table>
      </Panel>
    </div>
  </div>
</template>
<script>
import api from '@oj/api'
export default {
  name: 'DiscussionList',
  data () {
    return {
      loading: false,
      rows: [],
      columns: [
        {
          title: 'Question ID',
          render: (h, params) => {
            return h('a', {
              on: {
                click: () => {
                  this.$router.push({ name: 'problem-details', params: { problemID: params.row.problem_id } })
                }
              }
            }, params.row.problem_id)
          }
        },
        {
          title: 'Question Name',
          key: 'problem_title',
          render: (h, params) => {
            return h('span', params.row.problem_title ? params.row.problem_title.toUpperCase() : '')
          }
        },
        {
          title: 'User',
          key: 'username'
        },
        {
          title: 'Message',
          key: 'message'
        },
        {
          title: 'Time',
          render: (h, params) => {
            return h('span', new Date(params.row.create_time).toLocaleString())
          }
        }
      ]
    }
  },
  mounted () {
    this.fetch()
  },
  methods: {
    fetch () {
      this.loading = true
      api.getDiscussions().then(res => {
        this.rows = res.data.data
        this.loading = false
      }).catch((e) => {
        this.loading = false
        this.$Message.error('Failed to load discussions')
      })
    }
  }
}
</script>
<style scoped lang="less">
#main { flex: auto; margin-right: 18px; }
</style>
