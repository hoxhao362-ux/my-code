export const MANUSCRIPT_STATUS = {
  // 1. Initial Review Phase
  PENDING_INITIAL_REVIEW: 'pending_initial_review', // 待初审
  UNDER_INITIAL_REVIEW: 'under_initial_review', // 初审中 (Internal)
  INITIAL_REVIEW_PASSED: 'initial_review_passed', // 初审通过
  INITIAL_REVIEW_REVISION: 'initial_review_revision', // 初审退回修改
  INITIAL_REVIEW_REJECTED: 'initial_review_rejected', // 初审拒稿

  // 2. Peer Review Phase
  PENDING_PEER_REVIEW: 'pending_peer_review', // 待同行评审
  UNDER_PEER_REVIEW: 'under_peer_review', // 同行评审中
  REVIEW_COMPLETED: 'review_completed', // 评审完成 (待编辑处理)
  REVISION_REQUIRED: 'revision_required', // 需要修稿 (待作者修改)
  REVISION_SUBMITTED: 'revision_submitted', // 修订稿已提交

  // 3. Final Decision Phase
  PENDING_FINAL_DECISION: 'pending_final_decision', // 待终审 (Ready for EiC)
  UNDER_FINAL_DECISION: 'under_final_decision', // 终审中 (EiC reviewing)
  FINAL_DECISION_ACCEPTED: 'final_decision_accepted', // 终审通过 (Accepted)
  FINAL_DECISION_REVISION: 'final_decision_revision', // 终审修改后录用
  FINAL_DECISION_REJECTED: 'final_decision_rejected', // 终审拒稿

  // 4. Acceptance & Publication Phase
  PENDING_ACCEPTANCE_CONFIRMATION: 'pending_acceptance_confirmation', // 待录用确认
  PENDING_COPYRIGHT: 'pending_copyright', // 待版权协议签署
  PENDING_PROOF: 'pending_proof', // 待校样确认
  PENDING_PUBLICATION: 'pending_publication', // 待出版
  PUBLISHED: 'published', // 已出版
  WITHDRAWN: 'withdrawn' // 已撤稿
};

export const STATUS_LABELS = {
  [MANUSCRIPT_STATUS.PENDING_INITIAL_REVIEW]: 'Pending Initial Review',
  [MANUSCRIPT_STATUS.UNDER_INITIAL_REVIEW]: 'Under Initial Review',
  [MANUSCRIPT_STATUS.INITIAL_REVIEW_PASSED]: 'Initial Review Passed',
  [MANUSCRIPT_STATUS.INITIAL_REVIEW_REVISION]: 'Initial Review Revision',
  [MANUSCRIPT_STATUS.INITIAL_REVIEW_REJECTED]: 'Desk Rejected',
  [MANUSCRIPT_STATUS.REVIEW_COMPLETED]: 'Review Completed',
  [MANUSCRIPT_STATUS.REVISION_REQUIRED]: 'Revision Required',
  [MANUSCRIPT_STATUS.REVISION_SUBMITTED]: 'Revision Submitted',
  [MANUSCRIPT_STATUS.UNDER_PEER_REVIEW]: 'Under Peer Review',
  [MANUSCRIPT_STATUS.PENDING_FINAL_DECISION]: 'Pending Final Decision',
  [MANUSCRIPT_STATUS.UNDER_FINAL_DECISION]: 'Under Final Decision',
  [MANUSCRIPT_STATUS.FINAL_DECISION_ACCEPTED]: 'Accepted',
  [MANUSCRIPT_STATUS.FINAL_DECISION_REVISION]: 'Revision Required (Final)',
  [MANUSCRIPT_STATUS.FINAL_DECISION_REJECTED]: 'Rejected',
  [MANUSCRIPT_STATUS.PENDING_ACCEPTANCE_CONFIRMATION]: 'Pending Acceptance Confirmation',
  [MANUSCRIPT_STATUS.PENDING_COPYRIGHT]: 'Pending Copyright',
  [MANUSCRIPT_STATUS.PENDING_PROOF]: 'Pending Proof',
  [MANUSCRIPT_STATUS.PENDING_PUBLICATION]: 'Pending Publication',
  [MANUSCRIPT_STATUS.PUBLISHED]: 'Published',
  [MANUSCRIPT_STATUS.WITHDRAWN]: 'Withdrawn'
};

export const AUTHOR_STATUS_MAP = {
  [MANUSCRIPT_STATUS.PENDING_INITIAL_REVIEW]: 'Pending Initial Review',
  [MANUSCRIPT_STATUS.UNDER_INITIAL_REVIEW]: 'Pending Initial Review', // Hide internal
  [MANUSCRIPT_STATUS.INITIAL_REVIEW_PASSED]: 'Initial Review Passed',
  [MANUSCRIPT_STATUS.INITIAL_REVIEW_REVISION]: 'Revision Required',
  [MANUSCRIPT_STATUS.INITIAL_REVIEW_REJECTED]: 'Rejected',
  [MANUSCRIPT_STATUS.REVIEW_COMPLETED]: 'Under Review', // Hide internal detail
  [MANUSCRIPT_STATUS.REVISION_REQUIRED]: 'Revision Required',
  [MANUSCRIPT_STATUS.REVISION_SUBMITTED]: 'Revision Submitted',
  [MANUSCRIPT_STATUS.UNDER_PEER_REVIEW]: 'Under Peer Review',
  [MANUSCRIPT_STATUS.PENDING_FINAL_DECISION]: 'Pending Final Decision',
  [MANUSCRIPT_STATUS.UNDER_FINAL_DECISION]: 'Pending Final Decision', // Hide internal
  [MANUSCRIPT_STATUS.FINAL_DECISION_ACCEPTED]: 'Pending Acceptance Confirmation', // Wait for formal notice
  [MANUSCRIPT_STATUS.FINAL_DECISION_REVISION]: 'Revision Required',
  [MANUSCRIPT_STATUS.FINAL_DECISION_REJECTED]: 'Rejected',
  [MANUSCRIPT_STATUS.PENDING_ACCEPTANCE_CONFIRMATION]: 'Pending Acceptance Confirmation',
  [MANUSCRIPT_STATUS.PENDING_COPYRIGHT]: 'Pending Copyright',
  [MANUSCRIPT_STATUS.PENDING_PROOF]: 'Pending Proof',
  [MANUSCRIPT_STATUS.PENDING_PUBLICATION]: 'Pending Publication',
  [MANUSCRIPT_STATUS.PUBLISHED]: 'Published',
  [MANUSCRIPT_STATUS.WITHDRAWN]: 'Withdrawn'
};

export const STATUS_COLORS = {
  [MANUSCRIPT_STATUS.PENDING_INITIAL_REVIEW]: '#999999', // Light Gray
  [MANUSCRIPT_STATUS.UNDER_INITIAL_REVIEW]: '#4A90E2', // Light Blue
  [MANUSCRIPT_STATUS.INITIAL_REVIEW_PASSED]: '#28A745', // Green
  [MANUSCRIPT_STATUS.INITIAL_REVIEW_REVISION]: '#F5A623', // Orange
  [MANUSCRIPT_STATUS.INITIAL_REVIEW_REJECTED]: '#C93737', // Red
  [MANUSCRIPT_STATUS.REVIEW_COMPLETED]: '#4A90E2', // Light Blue
  [MANUSCRIPT_STATUS.REVISION_REQUIRED]: '#F5A623', // Orange
  [MANUSCRIPT_STATUS.REVISION_SUBMITTED]: '#4A90E2', // Light Blue
  [MANUSCRIPT_STATUS.UNDER_PEER_REVIEW]: '#4A90E2', // Light Blue
  [MANUSCRIPT_STATUS.PENDING_FINAL_DECISION]: '#999999', // Light Gray
  [MANUSCRIPT_STATUS.UNDER_FINAL_DECISION]: '#4A90E2', // Light Blue
  [MANUSCRIPT_STATUS.FINAL_DECISION_ACCEPTED]: '#28A745', // Green
  [MANUSCRIPT_STATUS.FINAL_DECISION_REVISION]: '#F5A623', // Orange
  [MANUSCRIPT_STATUS.FINAL_DECISION_REJECTED]: '#C93737', // Red
  [MANUSCRIPT_STATUS.PENDING_ACCEPTANCE_CONFIRMATION]: '#999999', // Light Gray
  [MANUSCRIPT_STATUS.PENDING_COPYRIGHT]: '#999999', // Light Gray
  [MANUSCRIPT_STATUS.PENDING_PROOF]: '#999999', // Light Gray
  [MANUSCRIPT_STATUS.PENDING_PUBLICATION]: '#999999', // Light Gray
  [MANUSCRIPT_STATUS.PUBLISHED]: '#1B5E20', // Dark Green
  [MANUSCRIPT_STATUS.WITHDRAWN]: '#333333' // Dark Gray
};
