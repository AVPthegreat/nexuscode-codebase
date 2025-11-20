<template>
  <Row type="flex" :gutter="24">
    <Col :span="18">
      <Card :padding="0" class="problem-list-card">
        <div slot="title" class="panel-header">
          <div class="title-text">{{$t('m.Problem_List')}}</div>
          <div class="filter-group">
            <Input v-model="query.keyword"
                   @on-enter="filterByKeyword"
                   placeholder="Search problems..."
                   icon="ios-search"
                   class="search-input"/>
            
            <Dropdown @on-click="filterByDifficulty" trigger="click" class="filter-dropdown">
              <Button type="ghost" class="filter-btn">
                {{query.difficulty === '' ? $t('m.Difficulty') : $t('m.' + query.difficulty)}}
                <Icon type="arrow-down-b"></Icon>
              </Button>
              <Dropdown-menu slot="list">
                <Dropdown-item name="">{{$t('m.All')}}</Dropdown-item>
                <Dropdown-item name="Low">{{$t('m.Low')}}</Dropdown-item>
                <Dropdown-item name="Mid">{{$t('m.Mid')}}</Dropdown-item>
                <Dropdown-item name="High">{{$t('m.High')}}</Dropdown-item>
              </Dropdown-menu>
            </Dropdown>

            <i-switch size="default" @on-change="handleTagsVisible" class="tag-switch">
              <span slot="open">{{$t('m.Tags')}}</span>
              <span slot="close">{{$t('m.Tags')}}</span>
            </i-switch>

            <Button type="text" @click="onReset" class="reset-btn">
              <Icon type="refresh"></Icon>
            </Button>
          </div>
        </div>
        
        <Table :columns="problemTableColumns"
               :data="problemList"
               :loading="loadings.table"
               class="problem-table"
               disabled-hover></Table>
               
        <div class="pagination-wrapper">
          <Pagination :total="total" 
                      :page-size.sync="query.limit" 
                      @on-change="pushRouter" 
                      @on-page-size-change="pushRouter" 
                      :current.sync="query.page" 
                      :show-sizer="true"></Pagination>
        </div>
      </Card>
    </Col>

    <Col :span="6">
      <Card :padding="20" class="sidebar-card">
        <div slot="title" class="sidebar-title">{{$t('m.Tags')}}</div>
        <div class="tag-list">
          <Button v-for="tag in tagList"
                  :key="tag.name"
                  @click="filterByTag(tag.name)"
                  type="ghost"
                  :class="{'active': query.tag === tag.name}"
                  size="small"
                  class="tag-btn">{{tag.name}}
          </Button>
        </div>
        
        <div class="sidebar-divider"></div>
        
        <Button type="primary" long size="large" @click="pickone" class="pick-one-btn">
          <Icon type="shuffle"></Icon>
          {{$t('m.Pick_One')}}
        </Button>
      </Card>
    </Col>
  </Row>
</template>

<script>
  import { mapGetters } from 'vuex'
  import api from '@oj/api'
  import utils from '@/utils/utils'
  import { ProblemMixin } from '@oj/components/mixins'
  import Pagination from '@oj/components/Pagination'

  export default {
    name: 'ProblemList',
    mixins: [ProblemMixin],
    components: {
      Pagination
    },
    data () {
      return {
        tagList: [],
        problemTableColumns: [
          {
            title: '#',
            key: '_id',
            width: 80,
            render: (h, params) => {
              return h('span', {
                style: {
                  color: 'var(--nexus-text-secondary)',
                  fontWeight: '600'
                }
              }, params.row._id)
            }
          },
          {
            title: this.$i18n.t('m.Title'),
            minWidth: 200,
            render: (h, params) => {
              return h('a', {
                style: {
                  fontWeight: '600',
                  fontSize: '15px',
                  color: 'var(--nexus-text-primary)'
                },
                on: {
                  click: () => {
                    this.$router.push({name: 'problem-details', params: {problemID: params.row._id}})
                  }
                }
              }, params.row.title)
            }
          },
          {
            title: this.$i18n.t('m.Level'),
            width: 120,
            render: (h, params) => {
              let t = params.row.difficulty
              let color = 'var(--nexus-info)'
              if (t === 'Low') color = 'var(--nexus-secondary)'
              else if (t === 'High') color = 'var(--nexus-accent)'
              
              return h('span', {
                style: {
                  color: color,
                  fontWeight: '600',
                  fontSize: '12px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px'
                }
              }, this.$i18n.t('m.' + params.row.difficulty))
            }
          },
          {
            title: this.$i18n.t('m.Total'),
            key: 'submission_number',
            width: 100
          },
          {
            title: this.$i18n.t('m.AC_Rate'),
            width: 120,
            render: (h, params) => {
              return h('span', this.getACRate(params.row.accepted_number, params.row.submission_number))
            }
          }
        ],
        problemList: [],
        limit: 20,
        total: 0,
        loadings: {
          table: true,
          tag: true
        },
        routeName: '',
        query: {
          keyword: '',
          difficulty: '',
          tag: '',
          page: 1,
          limit: 10
        }
      }
    },
    mounted () {
      this.init()
    },
    methods: {
      init (simulate = false) {
        this.routeName = this.$route.name
        let query = this.$route.query
        this.query.difficulty = query.difficulty || ''
        this.query.keyword = query.keyword || ''
        this.query.tag = query.tag || ''
        this.query.page = parseInt(query.page) || 1
        if (this.query.page < 1) {
          this.query.page = 1
        }
        this.query.limit = parseInt(query.limit) || 10
        if (!simulate) {
          this.getTagList()
        }
        this.getProblemList()
      },
      pushRouter () {
        this.$router.push({
          name: 'problem-list',
          query: utils.filterEmptyValue(this.query)
        })
      },
      getProblemList () {
        let offset = (this.query.page - 1) * this.query.limit
        this.loadings.table = true
        api.getProblemList(offset, this.limit, this.query).then(res => {
          this.loadings.table = false
          this.total = res.data.data.total
          this.problemList = res.data.data.results
          if (this.isAuthenticated) {
            this.addStatusColumn(this.problemTableColumns, res.data.data.results)
          }
        }, res => {
          this.loadings.table = false
        })
      },
      getTagList () {
        api.getProblemTagList().then(res => {
          this.tagList = res.data.data
          this.loadings.tag = false
        }, res => {
          this.loadings.tag = false
        })
      },
      filterByTag (tagName) {
        this.query.tag = tagName
        this.query.page = 1
        this.pushRouter()
      },
      filterByDifficulty (difficulty) {
        this.query.difficulty = difficulty
        this.query.page = 1
        this.pushRouter()
      },
      filterByKeyword () {
        this.query.page = 1
        this.pushRouter()
      },
      handleTagsVisible (value) {
        if (value) {
          this.problemTableColumns.push(
            {
              title: this.$i18n.t('m.Tags'),
              align: 'left',
              minWidth: 200,
              render: (h, params) => {
                let tags = []
                params.row.tags.forEach(tag => {
                  tags.push(h('Tag', {
                    props: {
                      color: 'default'
                    },
                    style: {
                      marginRight: '4px',
                      marginBottom: '4px'
                    }
                  }, tag))
                })
                return h('div', {
                  style: {
                    margin: '8px 0',
                    display: 'flex',
                    flexWrap: 'wrap'
                  }
                }, tags)
              }
            })
        } else {
          this.problemTableColumns.splice(this.problemTableColumns.length - 1, 1)
        }
      },
      onReset () {
        this.$router.push({name: 'problem-list'})
      },
      pickone () {
        api.pickone().then(res => {
          this.$success('Good Luck')
          this.$router.push({name: 'problem-details', params: {problemID: res.data.data}})
        })
      }
    },
    computed: {
      ...mapGetters(['isAuthenticated'])
    },
    watch: {
      '$route' (newVal, oldVal) {
        if (newVal !== oldVal) {
          this.init(true)
        }
      },
      'isAuthenticated' (newVal) {
        if (newVal === true) {
          this.init()
        }
      }
    }
  }
</script>

<style scoped lang="less">
  .problem-list-card {
    overflow: hidden;
    
    .panel-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px 24px;
      border-bottom: 1px solid var(--nexus-border);
      
      .title-text {
        font-size: 18px;
        font-weight: 700;
        color: var(--nexus-text-primary);
      }
      
      .filter-group {
        display: flex;
        align-items: center;
        gap: 12px;
        
        .search-input {
          width: 200px;
        }
        
        .filter-btn {
          color: var(--nexus-text-secondary);
          &:hover {
            color: var(--nexus-primary);
          }
        }
        
        .reset-btn {
          color: var(--nexus-text-secondary);
          &:hover {
            color: var(--nexus-primary);
          }
        }
      }
    }

    /deep/ .ivu-table-row {
      cursor: pointer;
    }
    
    .pagination-wrapper {
      padding: 20px;
      display: flex;
      justify-content: flex-end;
    }
  }
  
  .sidebar-card {
    .sidebar-title {
      font-size: 16px;
      font-weight: 600;
      color: var(--nexus-text-primary);
      margin-bottom: 16px;
    }
    
    .tag-list {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      
      .tag-btn {
        margin: 0;
        border: 1px solid var(--nexus-border);
        color: var(--nexus-text-secondary);
        
        &:hover, &.active {
          border-color: var(--nexus-primary);
          color: var(--nexus-primary);
          background: rgba(79, 70, 229, 0.05);
        }
      }
    }
    
    .tag-switch {
      margin-left: 10px;
      width: 90px;
      /deep/ .ivu-switch {
        width: 90px !important;
        &:after {
          left: 2px;
        }
        &.ivu-switch-checked:after {
          left: 68px;
        }
      }
    }
    
    .sidebar-divider {
      height: 1px;
      background: var(--nexus-border);
      margin: 20px 0;
    }
    
    .pick-one-btn {
      font-weight: 600;
      letter-spacing: 0.5px;
    }
  }
</style>
