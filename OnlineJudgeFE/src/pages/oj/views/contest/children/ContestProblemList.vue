<template>
  <div>
    <Panel>
      <div slot="title">{{$t('m.Problems_List')}}</div>
      <div slot="extra" v-if="contestStarted">
        <Button type="primary" size="small" @click="viewOverview">View Overview</Button>
      </div>
      <Table v-if="contestRuleType == 'ACM' || OIContestRealTimePermission"
             :columns="ACMTableColumns"
             :data="problems"
             @on-row-click="goContestProblem"
             :no-data-text="$t('m.No_Problems')"></Table>
      <Table v-else
             :data="problems"
             :columns="OITableColumns"
             @on-row-click="goContestProblem"
             no-data-text="$t('m.No_Problems')"></Table>
    </Panel>
  </div>
</template>

<script>
  import {mapState, mapGetters} from 'vuex'
  import {ProblemMixin} from '@oj/components/mixins'

  export default {
    name: 'ContestProblemList',
    mixins: [ProblemMixin],
    data () {
      return {
        ACMTableColumns: [
          {
            title: '#',
            key: '_id',
            sortType: 'asc',
            width: 150
          },
          {
            title: this.$i18n.t('m.Title'),
            key: 'title'
          },
          {
            title: this.$i18n.t('m.Total'),
            key: 'submission_number'
          },
          {
            title: this.$i18n.t('m.AC_Rate'),
            render: (h, params) => {
              return h('span', this.getACRate(params.row.accepted_number, params.row.submission_number))
            }
          }
        ],
        OITableColumns: [
          {
            title: '#',
            key: '_id',
            width: 150
          },
          {
            title: this.$i18n.t('m.Title'),
            key: 'title'
          }
        ]
      }
    },
    mounted () {
      this.getContestProblems()
      // Ensure scrolling works in fullscreen during contest
      if (this.$store.state.contest && this.$store.state.contest.started) {
        document.documentElement.style.overflow = 'auto'
        document.body.style.overflow = 'auto'
      }
    },
    methods: {
      getContestProblems () {
        this.$store.dispatch('getContestProblems').then(res => {
          if (this.isAuthenticated) {
            if (this.contestRuleType === 'ACM') {
              this.addStatusColumn(this.ACMTableColumns, res.data.data)
            } else if (this.OIContestRealTimePermission) {
              this.addStatusColumn(this.ACMTableColumns, res.data.data)
            }
          }
        })
      },
      goContestProblem (row) {
        this.$router.push({
          name: 'contest-problem-details',
          params: {
            contestID: this.$route.params.contestID,
            problemID: row._id
          }
        })
      },
      viewOverview () {
        this.$router.push({
          name: 'contest-details',
          params: {
            contestID: this.$route.params.contestID
          }
        })
      }
    },
    computed: {
      ...mapState({
        problems: state => state.contest.contestProblems
      }),
      ...mapGetters(['isAuthenticated', 'contestRuleType', 'OIContestRealTimePermission']),
      contestStarted () {
        return this.$store.state.contest && this.$store.state.contest.started
      }
    }
  }
</script>

<style scoped lang="less">
  /deep/ .ivu-table-row {
    cursor: pointer;
  }
</style>
