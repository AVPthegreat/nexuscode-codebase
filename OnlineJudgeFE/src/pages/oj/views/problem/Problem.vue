<template>
  <div class="flex-container">
    <div id="problem-main">
      <!--problem main-->
      <Panel :padding="40" shadow>
        <div slot="title">{{problem.title}}</div>
        <div id="problem-content" class="markdown-body" v-katex>
          <p class="title">{{$t('m.Description')}}</p>
          <p class="content" v-html=problem.description></p>
          <!-- {{$t('m.music')}} -->
          <p class="title">{{$t('m.Input')}} <span v-if="problem.io_mode.io_mode=='File IO'">({{$t('m.FromFile')}}: {{ problem.io_mode.input }})</span></p>
          <p class="content" v-html=problem.input_description></p>

          <p class="title">{{$t('m.Output')}} <span v-if="problem.io_mode.io_mode=='File IO'">({{$t('m.ToFile')}}: {{ problem.io_mode.output }})</span></p>
          <p class="content" v-html=problem.output_description></p>

          <div v-for="(sample, index) of problem.samples" :key="index">
            <div class="flex-container sample">
              <div class="sample-input">
                <p class="title">{{$t('m.Sample_Input')}} {{index + 1}}
                  <a class="copy"
                     v-clipboard:copy="sample.input"
                     v-clipboard:success="onCopy"
                     v-clipboard:error="onCopyError">
                    <Icon type="clipboard"></Icon>
                  </a>
                </p>
                <pre>{{sample.input}}</pre>
              </div>
              <div class="sample-output">
                <p class="title">{{$t('m.Sample_Output')}} {{index + 1}}</p>
                <pre>{{sample.output}}</pre>
              </div>
            </div>
          </div>

          <div v-if="problem.hint">
            <p class="title">{{$t('m.Hint')}}</p>
            <Card dis-hover>
              <div class="content" v-html=problem.hint></div>
            </Card>
          </div>

          <div v-if="problem.source">
            <p class="title">{{$t('m.Source')}}</p>
            <p class="content">{{problem.source}}</p>
          </div>

          <div class="editorial-section">
            <p class="title">Editorial</p>
            <div v-if="editorialLoading">
              <Spin size="large"></Spin>
            </div>
            <div v-else-if="editorialError">
              <Alert type="warning" show-icon>{{ editorialError }}</Alert>
            </div>
            <div v-else-if="editorial">
              <Card dis-hover>
                <div class="content" v-html="editorial"></div>
              </Card>
            </div>
            <div v-else>
              <Button type="primary" @click="loadEditorial" :loading="editorialLoading">
                View Editorial
              </Button>
            </div>
          </div>

        </div>
      </Panel>
      <!--problem main end-->
      <Card :padding="20" id="submit-code" dis-hover>
        <CodeMirror :value.sync="code"
                    :languages="problem.languages"
                    :language="language"
                    :theme="theme"
                    @resetCode="onResetToTemplate"
                    @changeTheme="onChangeTheme"
                    @changeLang="onChangeLang"></CodeMirror>
        <Row type="flex" justify="space-between">
          <Col :span="10">
            <div class="status" v-if="statusVisible">
              <template v-if="!this.contestID || (this.contestID && OIContestRealTimePermission)">
                <span>{{$t('m.Status')}}</span>
                <Tag type="dot" :color="submissionStatus.color" @click.native="handleRoute('/status/'+submissionId)">
                  {{$t('m.' + submissionStatus.text.replace(/ /g, "_"))}}
                </Tag>
              </template>
              <template v-else-if="this.contestID && !OIContestRealTimePermission">
                <Alert type="success" show-icon>{{$t('m.Submitted_successfully')}}</Alert>
              </template>
            </div>
            <div v-else-if="problem.my_status === 0">
              <Alert type="success" show-icon>{{$t('m.You_have_solved_the_problem')}}</Alert>
            </div>
            <div v-else-if="this.contestID && !OIContestRealTimePermission && submissionExists">
              <Alert type="success" show-icon>{{$t('m.You_have_submitted_a_solution')}}</Alert>
            </div>
            <div v-if="contestEnded">
              <Alert type="warning" show-icon>{{$t('m.Contest_has_ended')}}</Alert>
            </div>
          </Col>

          <Col :span="12">
            <template v-if="captchaRequired">
              <div class="captcha-container">
                <Tooltip v-if="captchaRequired" content="Click to refresh" placement="top">
                  <img :src="captchaSrc" @click="getCaptchaSrc"/>
                </Tooltip>
                <Input v-model="captchaCode" class="captcha-code"/>
              </div>
            </template>
            <Button type="warning" icon="edit" :loading="submitting" @click="submitCode"
                    :disabled="problemSubmitDisabled || submitted"
                    class="fl-right">
              <span v-if="submitting">{{$t('m.Submitting')}}</span>
              <span v-else>{{$t('m.Submit')}}</span>
            </Button>
          </Col>
        </Row>
      </Card>
    </div>


    <div id="right-column">
      <div v-if="contestStarted && contestID" class="contest-actions">
        <Button type="primary" long @click="handleViewOverview" style="margin-bottom: 8px;">View Overview</Button>
        <Button type="error" long @click="handleSubmitContest">Submit Contest</Button>
      </div>
      <div class="toggle-buttons grid-2x2">
        <Button class="toggle-btn" :type="activePanel==='info' ? 'primary' : 'default'" @click="activePanel='info'">
          <Icon type="information-circled" /> {{$t('m.Information')}}
        </Button>
        <Button class="toggle-btn" type="default" @click="goToSubmissions">
          <Icon type="navicon-round" /> {{$t('m.Submissions')}}
        </Button>
        <Button class="toggle-btn" :type="activePanel==='statistics' ? 'primary' : 'default'" @click="activePanel='statistics'">
          <Icon type="ios-analytics" /> {{$t('m.Statistic')}}
        </Button>
        <Button class="toggle-btn" :disabled="contestStarted" :type="activePanel==='discussion' ? 'primary' : 'default'" @click="activePanel='discussion'">
          <Icon type="chatbubble-working" /> Discussion
        </Button>
      </div>

      <div v-show="activePanel==='info'">
        <Card id="info">
          <div slot="title" class="header">
            <Icon type="information-circled"></Icon>
            <span class="card-title">{{$t('m.Information')}}</span>
          </div>
          <ul>
            <li><p>ID</p>
              <p>{{problem._id}}</p></li>
            <li>
              <p>{{$t('m.Time_Limit')}}</p>
              <p>{{problem.time_limit}}MS</p></li>
            <li>
              <p>{{$t('m.Memory_Limit')}}</p>
              <p>{{problem.memory_limit}}MB</p></li>
            <li>
              <p>{{$t('m.IOMode')}}</p>
              <p>{{problem.io_mode.io_mode}}</p>
            </li>
            <li>
              <p>{{$t('m.Created')}}</p>
              <p>{{problem.created_by.username}}</p></li>
            <li v-if="problem.difficulty">
              <p>{{$t('m.Level')}}</p>
              <p>{{$t('m.' + problem.difficulty)}}</p></li>
            <li v-if="problem.total_score">
              <p>{{$t('m.Score')}}</p>
              <p>{{problem.total_score}}</p>
            </li>
            <li>
              <p>{{$t('m.Tags')}}</p>
              <p>
                <Poptip trigger="hover" placement="left-end">
                  <a>{{$t('m.Show')}}</a>
                  <div slot="content">
                    <Tag v-for="tag in problem.tags" :key="tag">{{tag}}</Tag>
                  </div>
                </Poptip>
              </p>
            </li>
          </ul>
        </Card>
      </div>

      

      <div v-show="activePanel==='statistics'">
        <Card id="pieChart" :padding="0" v-if="!this.contestID || OIContestRealTimePermission">
          <div slot="title">
            <Icon type="ios-analytics"></Icon>
            <span class="card-title">{{$t('m.Statistic')}}</span>
            <Button type="ghost" size="small" id="detail" @click="graphVisible = !graphVisible">Details</Button>
          </div>
          <div class="echarts">
            <ECharts :options="pie"></ECharts>
          </div>
        </Card>
      </div>

      <div v-show="activePanel==='discussion'">
        <Card>
          <div slot="title">
            <Icon type="chatbubble-working" /> Discussion
          </div>
          <div>
            <Input v-model="discussionMessage" type="textarea" :rows="4" :maxlength="500" placeholder="Ask for help or report an issue..." />
            <div style="margin-top: 10px; text-align: right;">
              <Button type="primary" :disabled="!discussionMessage.trim() || contestStarted" @click="sendDiscussion">Send</Button>
            </div>
          </div>
        </Card>
      </div>
    </div>

    <Modal v-model="graphVisible">
      <div id="pieChart-detail">
        <ECharts :options="largePie" :initOptions="largePieInitOpts"></ECharts>
      </div>
      <div slot="footer">
        <Button type="ghost" @click="graphVisible=false">{{$t('m.Close')}}</Button>
      </div>
    </Modal>
  </div>
</template>

<script>
  import {mapGetters, mapActions} from 'vuex'
  import {types} from '../../../../store'
  import CodeMirror from '@oj/components/CodeMirror.vue'
  import storage from '@/utils/storage'
  import {FormMixin} from '@oj/components/mixins'
  import {JUDGE_STATUS, CONTEST_STATUS, buildProblemCodeKey} from '@/utils/constants'
  import api from '@oj/api'
  import {pie, largePie} from './chartData'

  // 只显示这些状态的图形占用
  const filtedStatus = ['-1', '-2', '0', '1', '2', '3', '4', '8']

  export default {
    name: 'Problem',
    components: {
      CodeMirror
    },
    mixins: [FormMixin],
    data () {
      return {
        statusVisible: false,
        captchaRequired: false,
        graphVisible: false,
        submissionExists: false,
        captchaCode: '',
        captchaSrc: '',
        contestID: '',
        problemID: '',
        submitting: false,
        code: '',
        language: 'C++',
        theme: 'solarized',
        submissionId: '',
        submitted: false,
        result: {
          result: 9
        },
        problem: {
          title: '',
          description: '',
          hint: '',
          my_status: '',
          template: {},
          languages: [],
          created_by: {
            username: ''
          },
          tags: [],
          io_mode: {'io_mode': 'Standard IO'}
        },
        pie: pie,
        largePie: largePie,
        // echarts 无法获取隐藏dom的大小，需手动指定
        largePieInitOpts: {
          width: '500',
          height: '480'
        },
        editorial: null,
        editorialLoading: false,
        editorialError: null,
        activePanel: 'info', // default panel
        discussionMessage: ''
      }
    },
    beforeRouteEnter (to, from, next) {
      let problemCode = storage.get(buildProblemCodeKey(to.params.problemID, to.params.contestID))
      if (problemCode) {
        next(vm => {
          vm.language = problemCode.language
          vm.code = problemCode.code
          vm.theme = problemCode.theme
        })
      } else {
        next()
      }
    },
    mounted () {
      this.$store.commit(types.CHANGE_CONTEST_ITEM_VISIBLE, {menu: false})
      // Ensure scrolling works in fullscreen during contest
      if (this.$store.state.contest && this.$store.state.contest.started) {
        document.documentElement.style.overflow = 'auto'
        document.body.style.overflow = 'auto'
      }
      
      // Set default editor theme based on global theme
      this.updateThemeFromGlobal()
      
      // Listen for theme changes
      this.themeObserver = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          if (mutation.attributeName === 'class') {
            this.updateThemeFromGlobal()
          }
        })
      })
      this.themeObserver.observe(document.body, { attributes: true })
      
      this.init()
    },
    beforeDestroy () {
      if (this.themeObserver) {
        this.themeObserver.disconnect()
      }
    },
    methods: {
      ...mapActions(['changeDomTitle']),
      updateThemeFromGlobal () {
        if (document.body.classList.contains('dark-mode')) {
          this.theme = 'material'
        } else {
          this.theme = 'solarized'
        }
      },
      handleViewOverview () {
        this.$router.push({ name: 'contest-details', params: { contestID: this.contestID } })
      },
      handleSubmitContest () {
        this.$Modal.confirm({
          title: 'Submit Contest',
          content: 'Are you sure you want to finish and submit the contest? You will be redirected to the overview page.',
          onOk: () => {
            // Submit all localStorage data to backend
            this.$store.dispatch('submitContestFromLocal', this.contestID).then(() => {
              this.$store.commit(types.CONTEST_RESET_LOCK, { contestID: this.contestID })
              document.documentElement.style.overflow = ''
              document.body.style.overflow = ''
              this.$Message.success('Contest submitted successfully')
              this.$router.push({ name: 'contest-details', params: { contestID: this.contestID } })
            }).catch(() => {
              this.$Message.error('Failed to submit contest')
            })
          }
        })
      },
      sendDiscussion () {
        const msg = this.discussionMessage.trim()
        if (!msg) { return }
        if (!this.$store.getters.isAuthenticated) {
          this.$Message.warning('Please login to post a discussion message')
          this.$store.dispatch('changeModalStatus', { mode: 'login', visible: true })
          return
        }
        const payload = { problem_id: this.problemID, message: msg }
        api.createDiscussion(payload).then(() => {
          this.$Message.success('Message sent')
          this.discussionMessage = ''
        }).catch((err) => {
          const msg = (err && err.data && err.data.data) || 'Failed to send message'
          this.$Message.error(msg)
        })
      },
      goToSubmissions () {
        this.$router.push(this.submissionRoute)
      },
      init () {
        this.$Loading.start()
        this.contestID = this.$route.params.contestID
        this.problemID = this.$route.params.problemID
        let func = this.$route.name === 'problem-details' ? 'getProblem' : 'getContestProblem'
        api[func](this.problemID, this.contestID).then(res => {
          this.$Loading.finish()
          let problem = res.data.data
          this.changeDomTitle({title: problem.title})
          api.submissionExists(problem.id).then(res => {
            this.submissionExists = res.data.data
          })
          problem.languages = problem.languages.sort()
          this.problem = problem
          if (problem.statistic_info) {
            this.changePie(problem)
          }

          // 在beforeRouteEnter中修改了, 说明本地有code，无需加载template
          if (this.code !== '') {
            return
          }
          // try to load problem template
          this.language = this.problem.languages[0]
          let template = this.problem.template
          if (template && template[this.language]) {
            this.code = template[this.language]
          }
        }, () => {
          this.$Loading.error()
        })
      },
      changePie (problemData) {
        // 只显示特定的一些状态
        for (let k in problemData.statistic_info) {
          if (filtedStatus.indexOf(k) === -1) {
            delete problemData.statistic_info[k]
          }
        }
        let acNum = problemData.accepted_number
        let data = [
          {name: 'WA', value: problemData.submission_number - acNum},
          {name: 'AC', value: acNum}
        ]
        this.pie.series[0].data = data
        // 只把大图的AC selected下，这里需要做一下deepcopy
        let data2 = JSON.parse(JSON.stringify(data))
        data2[1].selected = true
        this.largePie.series[1].data = data2

        // 根据结果设置legend,没有提交过的legend不显示
        let legend = Object.keys(problemData.statistic_info).map(ele => JUDGE_STATUS[ele].short)
        if (legend.length === 0) {
          legend.push('AC', 'WA')
        }
        this.largePie.legend.data = legend

        // 把ac的数据提取出来放在最后
        let acCount = problemData.statistic_info['0']
        delete problemData.statistic_info['0']

        let largePieData = []
        Object.keys(problemData.statistic_info).forEach(ele => {
          largePieData.push({name: JUDGE_STATUS[ele].short, value: problemData.statistic_info[ele]})
        })
        largePieData.push({name: 'AC', value: acCount})
        this.largePie.series[0].data = largePieData
      },
      handleRoute (route) {
        this.$router.push(route)
      },
      onChangeLang (newLang) {
        if (this.problem.template[newLang]) {
          if (this.code.trim() === '') {
            this.code = this.problem.template[newLang]
          }
        }
        this.language = newLang
      },
      onChangeTheme (newTheme) {
        this.theme = newTheme
      },
      onResetToTemplate () {
        this.$Modal.confirm({
          content: this.$i18n.t('m.Are_you_sure_you_want_to_reset_your_code'),
          onOk: () => {
            let template = this.problem.template
            if (template && template[this.language]) {
              this.code = template[this.language]
            } else {
              this.code = ''
            }
          }
        })
      },
      checkSubmissionStatus () {
        // 使用setTimeout避免一些问题
        if (this.refreshStatus) {
          // 如果之前的提交状态检查还没有停止,则停止,否则将会失去timeout的引用造成无限请求
          clearTimeout(this.refreshStatus)
        }
        const checkStatus = () => {
          let id = this.submissionId
          api.getSubmission(id).then(res => {
            this.result = res.data.data
            if (Object.keys(res.data.data.statistic_info).length !== 0) {
              this.submitting = false
              this.submitted = false
              clearTimeout(this.refreshStatus)
              
              // Update problem stats in localStorage if in contest
              if (this.contestID && this.$store.state.contest.started) {
                const submissionResult = res.data.data
                const info = submissionResult.info || {}
                const testcases = info.data || []
                const passedCases = testcases.filter(tc => tc.result === 0).length
                const totalCases = testcases.length
                
                this.$store.dispatch('updateProblemStatsLocal', {
                  contestID: this.contestID,
                  problemID: this.problemID,
                  stats: {
                    attempts: 1, // will be incremented in store
                    result: submissionResult.result,
                    passed_cases: passedCases,
                    total_cases: totalCases,
                    score: totalCases > 0 ? Math.floor((passedCases / totalCases) * 100) : 0
                  }
                })
              }
              
              this.init()
            } else {
              this.refreshStatus = setTimeout(checkStatus, 2000)
            }
          }, res => {
            this.submitting = false
            clearTimeout(this.refreshStatus)
          })
        }
        this.refreshStatus = setTimeout(checkStatus, 2000)
      },
      submitCode () {
        if (this.code.trim() === '') {
          this.$error(this.$i18n.t('m.Code_can_not_be_empty'))
          return
        }
        this.submissionId = ''
        this.result = {result: 9}
        this.submitting = true
        let data = {
          problem_id: this.problem.id,
          language: this.language,
          code: this.code,
          contest_id: this.contestID
        }
        if (this.captchaRequired) {
          data.captcha = this.captchaCode
        }
        const submitFunc = (data, detailsVisible) => {
          this.statusVisible = true
          api.submitCode(data).then(res => {
            this.submissionId = res.data.data && res.data.data.submission_id
            
            // Save submission to localStorage if in contest
            if (this.contestID && this.$store.state.contest.started) {
              this.$store.dispatch('saveSubmissionLocal', {
                contestID: this.contestID,
                submissionData: {
                  submission_id: this.submissionId,
                  problem_id: this.problem.id,
                  problem_title: this.problem.title,
                  language: this.language,
                  code: this.code,
                  result: 9 // pending initially
                }
              })
            }
            
            // 定时检查状态
            this.submitting = false
            this.submissionExists = true
            if (!detailsVisible) {
              this.$Modal.success({
                title: this.$i18n.t('m.Success'),
                content: this.$i18n.t('m.Submit_code_successfully')
              })
              return
            }
            this.submitted = true
            this.checkSubmissionStatus()
          }, res => {
            this.getCaptchaSrc()
            if (res.data.data.startsWith('Captcha is required')) {
              this.captchaRequired = true
            }
            this.submitting = false
            this.statusVisible = false
          })
        }

        if (this.contestRuleType === 'OI' && !this.OIContestRealTimePermission) {
          if (this.submissionExists) {
            this.$Modal.confirm({
              title: '',
              content: '<h3>' + this.$i18n.t('m.You_have_submission_in_this_problem_sure_to_cover_it') + '<h3>',
              onOk: () => {
                // 暂时解决对话框与后面提示对话框冲突的问题(否则一闪而过）
                setTimeout(() => {
                  submitFunc(data, false)
                }, 1000)
              },
              onCancel: () => {
                this.submitting = false
              }
            })
          } else {
            submitFunc(data, false)
          }
        } else {
          submitFunc(data, true)
        }
      },
      onCopy (event) {
        this.$success('Code copied')
      },
      onCopyError (e) {
        this.$error('Failed to copy code')
      },
      loadEditorial () {
        this.editorialLoading = true
        this.editorialError = null
        api.getProblemEditorial(this.problem.id).then(res => {
          this.editorial = res.data.data.editorial
          this.editorialLoading = false
        }).catch(err => {
          this.editorialLoading = false
          if (err.response && err.response.status === 403) {
            this.editorialError = 'You need to solve this problem first to view the editorial, or wait for the contest to end.'
          } else if (err.response && err.response.data && err.response.data.error) {
            this.editorialError = err.response.data.error
          } else {
            this.editorialError = 'Failed to load editorial. Please try again later.'
          }
        })
      }
    },
    computed: {
      ...mapGetters(['problemSubmitDisabled', 'contestRuleType', 'OIContestRealTimePermission', 'contestStatus']),
      contestStarted () { return this.$store.state.contest.started },
      contest () {
        return this.$store.state.contest.contest
      },
      contestEnded () {
        return this.contestStatus === CONTEST_STATUS.ENDED
      },
      submissionStatus () {
        return {
          text: JUDGE_STATUS[this.result.result]['name'],
          color: JUDGE_STATUS[this.result.result]['color']
        }
      },
      submissionRoute () {
        // Always pass the selected problemID for submissions
        if (this.contestID) {
          return {name: 'contest-submission-list', query: {problemID: this.problemID}}
        } else {
          return {name: 'submission-list', query: {problemID: this.problemID}}
        }
      }
    },
    beforeRouteLeave (to, from, next) {
      // 防止切换组件后仍然不断请求
      clearInterval(this.refreshStatus)

      this.$store.commit(types.CHANGE_CONTEST_ITEM_VISIBLE, {menu: true})
      storage.set(buildProblemCodeKey(this.problem._id, from.params.contestID), {
        code: this.code,
        language: this.language,
        theme: this.theme
      })
      next()
    },
    watch: {
      '$route' () {
        this.init()
      }
    }
  }
</script>

<style lang="less" scoped>
  .card-title {
    margin-left: 8px;
  }

  .flex-container {
    display: flex;
    align-items: flex-start;
    #problem-main {
      flex: auto;
      margin-right: 18px;
    }
    #right-column {
      flex: none;
      width: 220px;
      position: sticky;
      top: 90px; // keep entire right column fixed under navbar
      align-self: flex-start;
      max-height: calc(100vh - 100px);
      overflow: auto;
    }
  }

    #problem-content {
    margin-top: -50px;
    .title {
      font-size: 14px;
      font-weight: 700;
      margin: 25px 0 8px 0;
      color: var(--nexus-primary);
      text-transform: uppercase;
      .copy {
        padding-left: 8px;
      }
    }
    p.content {
      margin-left: 25px;
      margin-right: 20px;
      font-size: 15px
    }
    .sample {
      align-items: stretch;
      &-input, &-output {
        width: 50%;
        flex: 1 1 auto;
        display: flex;
        flex-direction: column;
        margin-right: 5%;
      }
      pre {
        flex: 1 1 auto;
        align-self: stretch;
        border-style: solid;
        background: transparent;
      }
    }
    .editorial-section {
      margin-top: 20px;
    }
  }

  #submit-code {
    margin-top: 20px;
    margin-bottom: 20px;
    .status {
      float: left;
      span {
        margin-right: 10px;
        margin-left: 10px;
      }
    }
    .captcha-container {
      display: inline-block;
      .captcha-code {
        width: auto;
        margin-top: -20px;
        margin-left: 20px;
      }
    }
  }

  #info {
    margin-bottom: 20px;
    margin-top: 20px;
    ul {
      list-style-type: none;
      li {
        border-bottom: 1px dotted #e9eaec;
        margin-bottom: 10px;
        p {
          display: inline-block;
        }
        p:first-child {
          width: 90px;
        }
        p:last-child {
          float: right;
        }
      }
    }
  }

  .fl-right {
    float: right;
  }

  #pieChart {
    .echarts {
      height: 250px;
      width: 210px;
    }
    #detail {
      position: absolute;
      right: 10px;
      top: 10px;
    }
  }

  #pieChart-detail {
    margin-top: 20px;
    width: 500px;
    height: 480px;
  }

  /* Toggle buttons layout: 2x2 grid and spacing to content (gap before dropdowns/sections) */
  .contest-actions {
    margin-bottom: 16px;
  }
  .toggle-buttons {
    margin-bottom: 20px; /* gap between buttons and the panels below */
    /* no need sticky here since whole column is sticky */
    z-index: 10;
    background: transparent; /* avoid covering content visually */
  }
  .grid-2x2 {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    grid-gap: 12px;
  }
  .toggle-btn {
    width: 100%;
  }
</style>

