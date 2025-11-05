<template>
  <Row type="flex">
    <Col :span="24">
    <Panel id="contest-card" shadow>
      <div slot="title">{{query.rule_type === '' ? this.$i18n.t('m.All') : query.rule_type}} {{$t('m.Contests')}}</div>
      <div slot="extra">
        <ul class="filter">
          <li>
            <Dropdown @on-click="onRuleChange">
              <span>{{query.rule_type === '' ? this.$i18n.t('m.Rule') : this.$i18n.t('m.' + query.rule_type)}}
                <Icon type="arrow-down-b"></Icon>
              </span>
              <Dropdown-menu slot="list">
                <Dropdown-item name="">{{$t('m.All')}}</Dropdown-item>
                <Dropdown-item name="OI">{{$t('m.OI')}}</Dropdown-item>
                <Dropdown-item name="ACM">{{$t('m.ACM')}}</Dropdown-item>
              </Dropdown-menu>
            </Dropdown>
          </li>
          <li>
            <Dropdown @on-click="onStatusChange">
              <span>{{query.status === '' ? this.$i18n.t('m.Status') : this.$i18n.t('m.' + CONTEST_STATUS_REVERSE[query.status].name.replace(/ /g,"_"))}}
                <Icon type="arrow-down-b"></Icon>
              </span>
              <Dropdown-menu slot="list">
                <Dropdown-item name="">{{$t('m.All')}}</Dropdown-item>
                <Dropdown-item name="0">{{$t('m.Underway')}}</Dropdown-item>
                <Dropdown-item name="1">{{$t('m.Not_Started')}}</Dropdown-item>
                <Dropdown-item name="-1">{{$t('m.Ended')}}</Dropdown-item>
              </Dropdown-menu>
            </Dropdown>
          </li>
          <li>
            <Input id="keyword" @on-enter="changeRoute" @on-click="changeRoute" v-model="query.keyword"
                   icon="ios-search-strong" placeholder="Keyword"/>
          </li>
        </ul>
      </div>
      <p id="no-contest" v-if="contests.length == 0">{{$t('m.No_contest')}}</p>
      <ol id="contest-list">
        <li v-for="contest in contests" :key="contest.title">
          <Card class="contest-card" :padding="12" dis-hover @click.native="goContest(contest)">
            <Row type="flex" justify="space-between" align="top">
              <Col :span="2" class="trophy-col">
                <img class="trophy" src="../../../../assets/Cup.png"/>
              </Col>
              <Col :span="16" class="contest-main">
                <p class="title">
                  <a class="entry" @click.stop="goContest(contest)">
                    {{contest.title}}
                  </a>
                  <template v-if="contest.contest_type != 'Public'">
                    <Icon type="ios-locked-outline" size="20"></Icon>
                  </template>
                </p>
                <ul class="detail vertical">
                  <li>
                    <Icon type="calendar" color="#3091f2"></Icon>
                    {{contest.start_time | localtime('DD-MM-YYYY HH:mm') }}
                  </li>
                  <li>
                    <Icon type="android-time" color="#3091f2"></Icon>
                    {{getDuration(contest.start_time, contest.end_time)}}
                  </li>
                  <li>
                    <Icon type="person" color="#3091f2"></Icon>
                    {{ (contest.created_by && contest.created_by.username) ? contest.created_by.username : 'Unknown' }}
                  </li>
                  <li>
                    <Button size="small" shape="circle" @click.stop="onRuleChange(contest.rule_type)">
                      {{contest.rule_type}}
                    </Button>
                  </li>
                </ul>
              </Col>
              <Col :span="6" class="status-col">
                <Tag type="dot" :color="CONTEST_STATUS_REVERSE[contest.status].color">{{ statusLabel(contest.status) }}</Tag>
              </Col>
            </Row>
          </Card>
        </li>
      </ol>
    </Panel>
    <Pagination :total="total" :page-size.sync="limit" @on-change="changeRoute" :current.sync="page" :show-sizer="true" @on-page-size-change="changeRoute"></Pagination>
    </Col>
  </Row>

</template>

<script>
  import api from '@oj/api'
  import { mapGetters } from 'vuex'
  import utils from '@/utils/utils'
  import Pagination from '@/pages/oj/components/Pagination'
  import time from '@/utils/time'
  import { CONTEST_STATUS_REVERSE, CONTEST_TYPE } from '@/utils/constants'

  const limit = 10

  export default {
    name: 'contest-list',
    components: {
      Pagination
    },
    data () {
      return {
        page: 1,
        query: {
          status: '',
          keyword: '',
          rule_type: ''
        },
        limit: limit,
        total: 0,
        rows: '',
        contests: [],
        CONTEST_STATUS_REVERSE: CONTEST_STATUS_REVERSE,
//      for password modal use
        cur_contest_id: ''
      }
    },
    beforeRouteEnter (to, from, next) {
      api.getContestList(0, limit).then((res) => {
        next((vm) => {
          vm.contests = res.data.data.results
          vm.total = res.data.data.total
        })
      }, (res) => {
        next()
      })
    },
    methods: {
      init () {
        let route = this.$route.query
        this.query.status = route.status || ''
        this.query.rule_type = route.rule_type || ''
        this.query.keyword = route.keyword || ''
        this.page = parseInt(route.page) || 1
        this.limit = parseInt(route.limit) || 10
        this.getContestList(this.page)
      },
      getContestList (page = 1) {
        let offset = (page - 1) * this.limit
        api.getContestList(offset, this.limit, this.query).then((res) => {
          let contests = res.data.data.results
          // Inject dummy contests for UI/UX validation as requested
          contests = contests.concat(this.generateDummyContests())
          // Sort: Running (0) first, Scheduled (1) in middle, Completed (-1) last
          this.contests = contests.sort((a, b) => {
            const order = { '0': 0, '1': 1, '-1': 2 }
            return (order[String(a.status)] || 999) - (order[String(b.status)] || 999)
          })
          this.total = res.data.data.total
        })
      },
      changeRoute () {
        let query = Object.assign({}, this.query)
        query.page = this.page
        query.limit = this.limit

        this.$router.push({
          name: 'contest-list',
          query: utils.filterEmptyValue(query)
        })
      },
      onRuleChange (rule) {
        this.query.rule_type = rule
        this.page = 1
        this.changeRoute()
      },
      onStatusChange (status) {
        this.query.status = status
        this.page = 1
        this.changeRoute()
      },
      goContest (contest) {
        this.cur_contest_id = contest.id
        if (contest.contest_type !== CONTEST_TYPE.PUBLIC && !this.isAuthenticated) {
          this.$error(this.$i18n.t('m.Please_login_first'))
          this.$store.dispatch('changeModalStatus', {visible: true})
        } else {
          this.$router.push({name: 'contest-details', params: {contestID: contest.id}})
        }
      },

      getDuration (startTime, endTime) {
        return time.duration(startTime, endTime)
      },
      statusLabel (statusCode) {
        // Map internal statuses to requested wording
        // 0 -> Running, 1 -> Scheduled, -1 -> Completed
        const map = {
          '0': 'Running',
          '1': 'Scheduled',
          '-1': 'Completed'
        }
        return map[String(statusCode)] || 'Scheduled'
      },
      generateDummyContests () {
        // Create 6 dummy contests with question id cb102 to test UI
        const now = new Date()
        const pad = (n) => (n < 10 ? '0' + n : '' + n)
        const addDays = (d, days) => new Date(d.getTime() + days * 86400000)
        const mkTime = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
        const statuses = ['0', '1', '-1', '1', '0', '-1']
        const rules = ['ACM', 'OI']
        const list = []
        for (let i = 0; i < 6; i++) {
          const start = addDays(now, -i)
          const end = addDays(start, 3)
          list.push({
            id: `dummy-${i}`,
            title: `CB102 Practice Contest #${i + 1}`,
            contest_type: 'Public',
            status: statuses[i % statuses.length],
            start_time: mkTime(start),
            end_time: mkTime(end),
            rule_type: rules[i % rules.length],
            created_by: { username: 'cb102-author' },
            question_id: 'CB102'
          })
        }
        return list
      }
    },
    computed: {
      ...mapGetters(['isAuthenticated', 'user'])
    },
    watch: {
      '$route' (newVal, oldVal) {
        if (newVal !== oldVal) {
          this.init()
        }
      }
    }

  }
</script>
<style lang="less" scoped>
  #contest-card {
    #keyword {
      width: 80%;
      margin-right: 30px;
    }
    #no-contest {
      text-align: center;
      font-size: 16px;
      padding: 20px;
    }
    #contest-list {
      /* Grid layout for contest cards */
      display: grid;
      grid-template-columns: repeat(3, 1fr);
  grid-gap: 12px;
      padding: 0;

      @media (max-width: 1200px) {
        grid-template-columns: repeat(2, 1fr);
      }
      @media (max-width: 700px) {
        grid-template-columns: 1fr;
      }

      > li {
        list-style: none;
        padding: 0;

        .contest-card {
          border-radius: 8px;
          overflow: hidden;
          cursor: pointer;
          transition: transform 0.25s ease-out, box-shadow 0.25s ease-out;
          will-change: transform, box-shadow;
          min-height: 150px;
          display: flex;
          flex-direction: column;

          /deep/ .ivu-card-body {
            flex: 1 1 auto;
            display: flex;
            flex-direction: column;
          }
          /* subtle lift */
          &:hover {
            transform: translateY(-2px) scale(1.03);
            box-shadow: 0 10px 24px rgba(0,0,0,0.18);
          }
        }

        .trophy-col {
          display: flex;
          align-items: flex-start;
          justify-content: center;
        }
        .trophy {
          height: 40px;
          margin: 4px 8px 0 0;
        }
        .contest-main {
          .title {
            font-size: 18px;
            a.entry {
              color: #495060;
              display: -webkit-box;
              line-clamp: 2;
              -webkit-line-clamp: 2;
              -webkit-box-orient: vertical;
              overflow: hidden;
              &:hover {
                color: #2d8cf0;
                border-bottom: 1px solid #2d8cf0;
              }
            }
          }
          .detail.vertical {
            display: block;
            padding-top: 4px;
            li {
              list-style: none;
              padding: 4px 0 0 0;
              display: flex;
              align-items: center;
              gap: 8px;
              white-space: nowrap;
            }
          }
        }
        .status-col {
          display: flex;
          align-items: flex-start;
          justify-content: flex-end;
          padding-top: 4px;
          
          /deep/ .ivu-tag {
            display: inline-flex;
            align-items: center;
            justify-content: flex-start;
            padding: 6px 14px;
            font-size: 12px;
            white-space: nowrap;
            line-height: 1.2;
            min-width: 100px;
          }
          
          /deep/ .ivu-tag-dot-inner {
            flex-shrink: 0;
            margin-right: 8px;
          }
        }
      }
    }
  }
</style>
