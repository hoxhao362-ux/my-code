export default {
  common: {
    journalName: 'Journal Name',
    ok: 'OK',
    cancel: 'Cancel',
    close: 'Close',
    confirm: 'Confirm',
    save: 'Save',
    delete: 'Delete',
    edit: 'Edit',
    search: 'Search',
    reset: 'Reset',
    view: 'View',
    back: 'Back',
    submit: 'Submit',
    loading: 'Loading...',
    noData: 'No data available',
    actions: 'Actions',
    status: 'Status',
    date: 'Date',
    title: 'Title',
    author: 'Author',
    module: 'Module',
    id: 'ID',
    abstract: 'Abstract',
    content: 'Content',
    references: 'References',
    next: 'Next',
    proceed: 'Proceed',
    select: 'Select...',
    saveLater: 'Save & Submit Later',
    required: 'Required',
    optional: 'Optional',
    add: 'Add',
    remove: 'Remove',
    download: 'Download',
    preview: 'Preview',
    success: 'Success',
    error: 'Error',
    warning: 'Warning',
    switchLang: 'Switch to Chinese'
  },
  progress: {
    step1: 'Article Type',
    step2: 'Attach Files',
    step3: 'General Information',
    step4: 'Additional Information',
    step5: 'Comments',
    step6: 'Manuscript Data',
  },
  articleTypeSelection: {
    title: 'Article Type Selection',
    label: 'Article Type',
    placeholder: 'Select article type',
    types: {
      invited: 'Invited Article',
      correspondence: 'Correspondence',
      comments: 'Comments',
      clinical: 'Clinical Rounds',
      original: 'Original Research',
      review: 'Review Article'
    },
    guidelinesTitle: 'Submission Guidelines for Selected Type',
    guidelines: {
      general: 'Submission Guidelines',
      wordCount: 'Word Count Limit',
      references: 'Reference Count Requirements',
    },
    errors: {
      required: 'Please select an article type',
    },
  },
  attachFiles: {
    title: 'Attach Files',
    dragDrop: 'Drag and drop files here, or click to browse',
    browse: 'Browse',
    bulkUpdate: 'Bulk update file types',
    fileType: 'File Type',
    fileName: 'File Name',
    description: 'Description',
    actions: 'Actions',
    types: {
      manuscript: 'Manuscript',
      contribution: 'Author Contribution',
      conflict: 'Conflict of Interest',
      figure: 'Figure',
      table: 'Table',
      supplementary: 'Supplementary Material'
    },
    placeholders: {
      description: 'Enter custom file description (optional)',
      selectType: 'Select type'
    },
    confirmDelete: 'Are you sure you want to delete this file? This action cannot be undone.',
    errors: {
      noFile: 'Please upload at least one manuscript-related file',
    },
    requiredFiles: {
      title: 'Required Files',
      description: 'The following files are mandatory for submission. Please ensure each type has at least one file uploaded.',
      descriptions: {
        manuscript: 'Contains title, abstract, main text, references, and tables. This is the core document of your submission.',
        contribution: 'Specifies each author\'s individual contributions following ICMJE guidelines. Essential for academic integrity.',
        conflict: 'Discloses all potential competing interests to ensure research objectivity.'
      },
      missingWarning: 'Missing required files: ',
      missingError: 'Please upload all required files: Manuscript, Author Contribution, and Conflict of Interest.',
      allUploaded: 'All required files have been uploaded.'
    }
  },
  generalInformation: {
    title: 'General Information',
    subjectLabel: 'Subject / Discipline',
    subjectPlaceholder: 'Select the primary subject',
    keywordsLabel: 'Keywords',
    keywordsHelper: 'Enter keywords separated by commas (e.g., COVID-19, Vaccine, mRNA)',
    keywordsPlaceholder: 'Enter 3-5 keywords',
    errors: {
      subjectRequired: 'Subject selection is required.',
      keywordsRequired: 'Please provide at least one keyword.',
    },
  },
  additionalInformation: {
    title: 'Additional Information',
    questions: {
      q1: 'Confirm data access and responsibility for submission',
      q2: 'Have all authors reviewed and agreed to the submission?',
      q3: 'Was a medical author/editor involved, and provide funding details',
      q4: 'Which authors accessed and verified study data, who is responsible for the submission decision?',
      q5: 'Was generative AI used, please explain the specific use',
      q6: 'Provide manuscript word count, reference count, and figure/table count',
    },
    ssrn: 'Agree to publish research article on SSRN preprint platform',
    socialMedia: "Corresponding author's social media handles",
    conference: 'Simultaneous submission to future conferences confirmation',
    errors: {
      incomplete: 'Please complete all additional information questions',
      limitExceeded: 'Input exceeds character limit, please shorten the content',
    },
  },
  comments: {
    title: 'Comments',
    coverLetter: 'Cover Letter (Notes to the journal, will not appear in the final manuscript)',
    placeholder: 'Enter notes to the journal, e.g., manuscript highlights, submission notes, etc.',
    additionalComments: 'Additional Comments',
    commentsPlaceholder: 'Any additional notes or comments for the editorial office',
    errors: {
      required: 'Please enter a cover letter for the journal',
    },
  },
  manuscriptData: {
    title: 'Manuscript Data',
    manuscriptTitle: 'Title (Manuscript Title)',
    abstract: 'Abstract',
    keywords: 'Keywords',
    keywordsPlaceholder: 'Enter keywords, separated by commas',
    authors: {
      title: 'Authors',
      add: 'Add Author',
      name: 'Name',
      institution: 'Institution',
      email: 'Email',
      corresponding: 'Corresponding Author',
      first: 'First Author',
    },
    funding: {
      title: 'Funding Information',
      add: 'Add Funding Source',
      noFunding: 'No funding information',
      body: 'Funding Body',
      selectBody: 'Select funding body',
      number: 'Grant Number',
    },
    buildPDF: 'Build PDF for Approval',
    previewTitle: 'PDF Preview',
    publishingOption: {
      title: 'Publishing Option',
      subscription: 'Subscription (Subscription model)',
      openAccess: 'Open Access (Open access model)',
    },
    errors: {
      incomplete: 'Please complete all required fields',
      noAuthor: 'Please add at least one author',
      noCorresponding: 'Please select a corresponding author',
      noFirst: 'Please select a first author',
      noFunding: 'Please add funding information or select "No funding information"',
    },
    successMessage: 'Submission has been successfully submitted. Please wait for initial review',
  },
  submissionRules: {
    title: 'Submission Guidelines',
    intro: 'Please read the following guidelines carefully before submitting...',
    format: 'Format',
    formatDesc: 'PDF, Word, or LaTeX.',
    authors: 'Authors',
    authorsDesc: 'Ensure all authors are listed and have approved the submission.',
    originality: 'Originality',
    originalityDesc: 'Content must be original.',
    start: 'Start Submission'
  },
  editor: {
    manuscripts: {
      title: 'Manuscript Management',
      currentRole: 'Current Role',
      tabs: {
        all: 'All Manuscripts',
        assigned: 'My Assigned',
        pending: 'Pending Action'
      },
      search: {
        placeholder: 'Search by ID, title, author or field...',
        history: 'Search History',
        clear: 'Clear History'
      },
      filter: {
        status: 'Status',
        dateRange: 'Date Range',
        author: 'Author Name',
        field: 'Field',
        reset: 'Reset Filters',
        advanced: 'Advanced Filters'
      },
      dateRanges: {
        custom: 'Custom Range',
        today: 'Today',
        thisWeek: 'This Week',
        thisMonth: 'This Month',
        thisYear: 'This Year'
      },
      columns: {
        id: 'ID',
        title: 'Title',
        author: 'Author',
        date: 'Submitted Date',
        status: 'Status',
        actions: 'Actions'
      },
      actions: {
        view: 'View',
        assign: 'Assign Reviewers',
        initialReview: 'Initial Review',
        reviewSummary: 'Review Summary',
        finalDecision: 'Make Decision',
        revisionCheck: 'Check Revision',
        auditLog: 'Audit Log',
        history: 'History',
        deskReject: 'Desk Reject',
        withdraw: 'Withdraw',
        archive: 'Archive',
        sendProduction: 'Send to Production',
        formatCheck: 'Format Check'
      },
      alerts: {
        noPermission: 'Permission denied',
        deskReject: 'Desk Reject Confirmed',
        withdraw: 'Manuscript Withdrawn',
        archive: 'Manuscript Archived',
        production: 'Sent to Production',
        formatCheck: 'Format Check Completed',
        initialReview: 'Initial Review Completed: {decision}',
        reviewSummary: 'Review Summary Report Generated & Submitted to EiC',
        materialsSubmitted: 'Materials submitted to Editor-in-Chief',
        finalDecision: 'Final Decision Submitted: {decision}',
        revisionPassed: 'Revision Passed',
        revisionReturned: 'Returned for Revision',
        revisionRejected: 'Revision Rejected'
      },
      back: '← Back to Dashboard',
      noManuscripts: 'No manuscripts found matching your criteria'
    },
    reviewers: {
      title: 'Reviewer Management Module',
      currentRole: 'Current Role',
      table: {
        name: 'Name',
        email: 'Email',
        expertise: 'Expertise',
        status: 'Status',
        actions: 'Actions'
      }
    },
    audit: {
      newSubmissions: {
        title: 'New Submissions',
        subtitle: 'Screening & Initial Check',
        columns: {
          author: 'Author',
          date: 'Date',
          module: 'Module',
          actions: 'Actions'
        },
        links: {
          viewManuscript: 'View Manuscript',
          viewAttachments: 'View Attachments',
          ethicsStatement: 'Ethics Statement'
        },
        actions: {
          screen: 'Screen & Send',
          transfer: 'Suggest Transfer',
          reject: 'Reject'
        },
        noData: 'No new submissions pending screening.',
        modals: {
          screen: {
            title: 'Screen & Send Confirmation',
            notesLabel: 'Initial Screening Notes (Optional)',
            notesPlaceholder: 'Enter brief screening notes (optional)',
            assignmentLabel: 'Assignment Options',
            autoAssign: 'Auto-assign to Assign Reviewers task pool',
            specificAssign: 'Assign to specific editor',
            noEditors: 'No active editors are available for manual assignment. This manuscript will be auto-assigned to the Assign Reviewers task pool.',
            selectEditor: 'Select Editor',
            loadingEditors: 'Loading editors...',
            noActiveEditors: 'No active editors available',
            confirmBtn: 'Confirm & Proceed'
          },
          transfer: {
            title: 'Suggest Transfer to Another Journal',
            reasonLabel: 'Transfer Reason',
            reasonPlaceholder: 'Enter reason for transfer suggestion (required)',
            journalLabel: 'Journal Selection',
            previewLabel: 'Transfer Letter Preview',
            letterTemplate: 'Dear {author},\n\nWe have reviewed your manuscript "{title}". While it is of high quality, we believe it would be better suited for our sister journal, {targetJournal}.\n\nBest regards,\nThe {journalName} Editorial Team',
            sendBtn: 'Send Transfer Suggestion'
          },
          reject: {
            title: 'Reject Manuscript (Desk Reject)',
            reasonLabel: 'Rejection Reasons (Select all that apply)',
            categories: {
              scope: 'Scope & Novelty',
              methodology: 'Methodology',
              presentation: 'Presentation & Other'
            },
            reasons: {
              outOfScope: 'Out of scope for this journal',
              insufficientNovelty: 'Insufficient novelty or originality',
              methodologicalFlaws: 'Major methodological flaws',
              statisticalErrors: 'Statistical errors',
              poorPresentation: 'Poor presentation or language quality'
            },
            otherLabel: 'Other Reason (Please specify)',
            commentsLabel: 'Editor Comments (Sent to Author)',
            commentsPlaceholder: 'Provide detailed feedback for the author...',
            templateLabel: 'Letter Template',
            templates: {
              standard: 'Standard Template',
              custom: 'Custom Template'
            },
            confirmBtn: 'Confirm Rejection'
          },
          manuscript: {
            title: 'Manuscript Preview',
            zoomIn: 'Zoom In',
            zoomOut: 'Zoom Out',
            prevPage: 'Previous Page',
            nextPage: 'Next Page',
            fullScreen: 'Full Screen',
            exitFullScreen: 'Exit Full Screen'
          },
          attachments: {
            title: 'Supplementary Materials & Attachments',
            refresh: 'Refresh List',
            downloadAll: 'Download All (ZIP)',
            preview: 'Preview',
            download: 'Download',
            noAttachments: 'No supplementary materials uploaded for this manuscript.',
            groups: {
              supplementary: 'Supplementary Materials',
              figures: 'Figures & Tables'
            }
          },
          ethics: {
            title: 'Ethics & Compliance Statement',
            verified: 'Ethics Verified',
            pending: 'Pending Verification',
            verifyBtn: 'Verify Statement',
            unverifyBtn: 'Unverify Statement',
            requestRevision: 'Request Ethics Revision',
            print: 'Print Statement',
            sections: {
              irb: 'IRB Approval',
              consent: 'Informed Consent',
              data: 'Data Sharing'
            },
            mockData: {
              irb: 'This study was approved by the Institutional Review Board of [Hospital Name] (Approval No. IRB-2023-001) on January 15, 2023.',
              consent: 'Written informed consent was obtained from all participants prior to their inclusion in the study.',
              data: 'De-identified participant data will be made available upon reasonable request to the corresponding author.'
            }
          },
          validation: {
            title: 'Required Selection Missing',
            message: 'Please select an editor to assign this manuscript to before proceeding.'
          }
        },
        detail: {
          backToList: '← Back to List',
          id: 'ID:',
          status: 'Status:',
          submitted: 'Submitted:',
          tabs: {
            preview: 'Revision Preview (Track Changes)',
            response: 'Point-by-Point Response'
          },
          preview: {
            simulationNote: '[Simulation] Displaying Revised Manuscript with Track Changes...',
            introduction: 'Introduction',
            trackChanges: 'The {old} {new} methodology implementation shows significant improvement...',
            reviewedLabel: 'I have reviewed the revision content.'
          },
          response: {
            originalComments: 'Original Reviewer Comments (Anonymized)',
            authorResponse: "Author's Response",
            responseTo: 'Response to {reviewer}',
            authorLabel: 'Author:',
            thankYou: 'Thank you for your comment. We have addressed this by...',
            updatedFigure: 'As requested, we have updated Figure 2 and clarified the methodology section (lines 145-150).'
          },
          actions: {
            reject: 'Reject',
            requestFurther: 'Request Further Revision',
            approve: 'Approve'
          },
          modals: {
            approve: {
              title: 'Confirm Action: APPROVE',
              msg: 'Are you sure you want to approve this revision? The manuscript will proceed to the next stage (e.g., final acceptance).',
              reviewRequired: 'Please review the revision before approving.'
            },
            sendRequest: {
              title: 'Confirm Action: SEND_REQUEST',
              draftMsg: 'Draft Revision Request for Manuscript ID: {id}',
              commentsSummary: 'Reviewer Comments Summary (Anonymized)',
              revisionType: 'Revision Type:',
              deadline: 'Deadline:',
              types: {
                minor: 'Minor Revision',
                major: 'Major Revision'
              },
              requirementsLabel: 'Revision Requirements / Editor Comments:',
              requirementsTip: 'Please summarize your editorial decision and provide clear guidance to the author on how to address the reviewer comments.',
              declaration: {
                title: 'Editorial Declaration',
                reviewedComments: 'I have reviewed all reviewer comments and ensured they are accurately reflected in this request.',
                deadlineGuidelines: 'The revision deadline is set in accordance with the Peerex Peer editorial guidelines.',
                scopePolicy: 'I confirm that this revision request is consistent with the journal policies.'
              },
              tooltips: {
                provideComments: 'Please provide editorial comments before sending the request.',
                confirmDeclarations: 'Please confirm all editorial declarations before sending the request.'
              },
              doubleConfirm: {
                title: 'Confirm Send Request',
                msg: 'Are you sure you want to send this revision request to the author?',
                note: "The manuscript status will be updated to 'Revision Required' and the author will be notified."
              }
            },
            reject: {
              title: 'Confirm Action: REJECT',
              areYouSure: 'Are you sure you want to Reject the revision for Manuscript ID: {id}?',
              reasonLabel: 'Rejection Reason:',
              reasonTip: 'Please provide a clear reason for rejecting this revision. This will be sent to the author.',
              reasonRequiredTooltip: 'Please provide a clear reason for rejecting this revision.',
              doubleConfirm: {
                title: 'High Risk Action',
                msg: 'WARNING: This action will reject the manuscript and terminate the review process. Are you absolutely sure?',
                confirmBtn: 'Yes, Reject Manuscript'
              }
            }
          }
        },
        alerts: {
          previewUnavailable: 'Preview Unavailable\n\nThis file type is not supported for preview. Please download to view.',
          downloadStarted: 'Download started for all attachments.',
          revisionSent: 'Revision request sent to author.',
          downloading: 'Downloading {name}...',
          assignmentFailed: 'Assignment failed. Please try again.',
          screenConfirmed: 'Screening confirmed. Manuscript moved to next stage.',
          transferReasonRequired: 'Please enter a reason for transfer.',
          transferSent: 'Transfer suggestion sent to author.',
          fieldsRequired: 'Please fill in all required fields.',
          specifyOther: 'Please specify the other reason.',
          rejectConfirmed: 'Rejection confirmed. Manuscript marked as Desk Rejected.'
        }
      },
      assignReviewers: {
        title: 'Assign Reviewers',
        subtitle: 'Select and Invite Peer Reviewers',
        tabs: {
          authorRecommended: 'Author Recommended',
          smartRecommendation: 'Smart Recommendation',
          manualSearch: 'Manual Search'
        },
        noAuthorRecommendations: 'No author recommendations found for this manuscript.',
        authorRecommendationHint: 'Please ensure the author has submitted suggestions, or use Smart Recommendation / Manual Search.',
        reason: 'Reason',
        searchPlaceholder: 'Search reviewers...',
        filters: {
          all: 'All',
          matchField: 'Match Field'
        },
        selectionCount: 'Selected: {count}',
        noManuscripts: 'No manuscripts waiting for reviewer assignment.',
        modalTitle: 'Select Reviewers',
        meta: {
          author: 'Author',
          module: 'Module'
        },
        actions: {
          assign: 'Assign Reviewers',
          reinvite: 'Re-invite',
          confirm: 'Confirm Assignment'
        },
        alerts: {
          selectAtLeastOne: 'Please select at least one reviewer.',
          assignedSuccess: 'Reviewers assigned. {count} invitations sent. Manuscript moved to "Under Review".',
          reinviteHint: 'Re-invitation feature would go here.'
        }
      },
      reviewMonitoring: {
        title: 'Review Monitoring',
        subtitle: 'Track Progress & Manage Delays',
        meta: {
          author: 'Author',
          sentToReview: 'Sent to Review'
        },
        reviewerStatus: 'Reviewers Status',
        actions: {
          remind: 'Remind',
          replace: 'Replace',
          processExtension: 'Process Extension Request'
        },
        status: {
          invited: 'Invited',
          accepted: 'Accepted',
          declined: 'Declined',
          overdue: 'Overdue'
        },
        noManuscripts: 'No manuscripts currently under review.',
        noReviewers: 'No reviewers assigned yet (Data inconsistency).',
        alerts: {
          reminderSent: 'Reminder sent to {name}.',
          replaceConfirm: 'Replace reviewer {name}?',
          redirecting: 'Redirecting to replacement selection (mock)...',
          extensionGranted: 'Extension granted for 7 days.'
        }
      },
      decisionMaking: {
        title: 'Decision Central',
        subtitle: 'Evidence-Based Decision Making System',
        tabs: {
          consolidation: 'Review Consolidation',
          consensus: 'Consensus Meetings',
          appeals: 'Appeals & Rebuttals'
        },
        consolidation: {
          noManuscripts: 'No manuscripts pending consolidation.',
          reviewerOpinions: 'Reviewer Opinions',
          reviewerLabel: 'Reviewer',
          score: 'Score',
          noReviews: 'No reviews data available.',
          assessment: "Editor's Assessment",
          systemAnalysis: 'System Analysis',
          consensusLevel: 'Consensus Level',
          mixed: 'Mixed',
          high: 'High',
          keyIssues: 'Key Issues',
          detected: 'Detected',
          actions: {
            draftDecision: 'Draft Decision & Rationale',
            requestConsensus: 'Request Consensus Meeting'
          }
        },
        consensus: {
          noManuscripts: 'No manuscripts scheduled for consensus meeting.',
          scheduleNew: 'Schedule New Meeting',
          nextMeeting: 'Next Meeting',
          reasonLabel: 'Reason for Meeting',
          actions: {
            finalize: 'Finalize Decision',
            viewMinutes: 'View Minutes'
          }
        },
        appeals: {
          noAppeals: 'No active appeals.',
          reasonLabel: 'Appeal Reason',
          actions: {
            assignIndependent: 'Assign Independent Reviewer'
          }
        },
        modals: {
          decision: {
            title: 'Final Decision',
            sections: {
              decision: '1. Decision',
              rationale: '2. Evidence-Based Rationale',
              letter: '3. Decision Letter to Author'
            },
            types: {
              accept: 'Accept (Publish without further changes)',
              minor: 'Minor Revision (Back to Author - Editor Check Only)',
              major: 'Major Revision (Back to Author - Re-review Required)',
              return: 'Return to Reviewer (Special Case: Direct Re-review)',
              reject: 'Reject (Decline Submission)',
              transfer: 'Transfer (Recommend Other Journals)',
              consensus: 'Escalate to Consensus Meeting'
            },
            returnWarning: 'This option bypasses the author and sends the manuscript directly back to reviewers. Use only for arbitration or internal re-evaluation.',
            rationaleLabels: {
              rigor: 'Scientific Rigor',
              novelty: 'Novelty & Innovation',
              methodology: 'Methodology',
              dataIntegrity: 'Data Integrity'
            },
            placeholders: {
              rigor: 'Comment on study design and controls...',
              novelty: 'Comment on contribution to the field...',
              methodology: 'Comment on methods...',
              dataIntegrity: 'Comment on data quality...',
              letter: 'Draft your letter here. The structured rationale above will be attached for internal records.'
            }
          }
        },
        alerts: {
          onlyEditors: 'Only editors can handle manuscripts pending final decision.',
          enterComments: 'Please enter decision comments.',
          movedToConsensus: 'Manuscript moved to Consensus Meeting queue.',
          decisionRecorded: 'Decision recorded: {type}.',
          sentToEIC: 'Manuscript sent to Editor-in-Chief for final decision.',
          letterGenerated: "Draft letter generated in 'Decisions & Letters' module.",
          meetingScheduled: 'Meeting scheduled for {title}. Notification sent to attendees.',
          independentAssigned: 'Independent reviewer assigned for appeal of {title}.'
        }
      },
      revisionHandling: {
        title: 'Revision Handling',
        subtitle: 'Peerex Peer-Style Revision Audit & Control',
        columns: {
          id: 'MS ID',
          title: 'Title',
          version: 'Version',
          deadline: 'Deadline',
          status: 'Status',
          formatCheck: 'Format Check',
          actions: 'Actions'
        },
        noManuscripts: 'No pending revisions found.',
        formatCheck: {
          title: 'Format Compliance Check',
          verifyItems: 'Please verify the following items for the revision ({version}):',
          checklist: {
            wordCount: 'Manuscript word count limits',
            abstract: 'Abstract structure (Background, Methods, Findings, Interpretation)',
            coi: 'Conflict of Interest declaration',
            figures: 'Figure quality and legends',
            references: 'Reference formatting (Vancouver style)'
          },
          passBtn: 'Confirm & Pass',
          runCheck: 'Run Check',
          passed: '✔ Passed'
        },
        reReview: {
          title: 'Coordinate Re-Review',
          selectReviewers: 'Select reviewers for this round of revision:',
          sendBtn: 'Send to Selected Reviewers'
        },
        actions: {
          preview: 'Preview',
          approve: 'Approve',
          reReview: 'Re-Review',
          returnForRevision: 'Return for Revision'
        },
        preview: {
          title: 'Preview: Manuscript ID {id}',
          tabs: {
            reviewerComments: 'Reviewer Comments',
            manuscriptPreview: 'Manuscript Preview',
            revisionHistory: 'Revision History'
          },
          noContent: 'No preview content available for this manuscript at this stage.',
          noHistory: 'No revision history available for this manuscript.',
          openDetail: 'Open Full Audit Detail'
        },
        modals: {
          confirmAction: 'Confirm Action: {action}',
          areYouSure: 'Are you sure you want to {action} the revision for Manuscript ID: {id}?',
          editorComment: 'Editor Comment / Decision Rationale:',
          editorCommentsOptional: 'Editor Comments (Optional):',
          approveRationale: 'Please document the rationale for approving this manuscript.',
          rejectRationale: 'Please provide a clear and constructive reason for returning this manuscript for revision.',
          commentPlaceholder: 'Enter comments for the author...',
          confirmBtn: 'Confirm {action}',
          doubleConfirm: {
            approveTitle: 'Confirm Approval',
            rejectTitle: 'Confirm Return for Revision',
            approveMsg: 'Are you sure you want to approve this manuscript?',
            rejectMsg: 'WARNING: You are about to return this manuscript for revision. Are you sure?'
          }
        },
        alerts: {
          allChecksRequired: 'All format checks must be passed before proceeding.',
          formatPassed: 'Format check passed. You may now proceed with the review process.',
          auditSuccess: 'Manuscript {id} has been {action}.',
          sentToReviewers: 'Sent back to reviewers: {reviewers}',
          notification: {
            approvedTitle: 'Revision Approved',
            rejectedTitle: 'Revision Rejected',
            statusUpdateTitle: 'Revision Status Update',
            reReviewTitle: 'Re-Review Request',
            approvedMsg: 'Your revision for MS {id} has been approved and sent to decision making. Editor Comment: {comment}',
            rejectedMsg: 'The revision did not address reviewer comments adequately. Please revise and resubmit. Editor Comment: {comment}',
            reReviewMsg: 'Your manuscript has been sent back to reviewers for further evaluation.',
            reviewerMsg: 'Manuscript {id} has been returned for re-review. Please check your assignments.'
          }
        }
      }
    }
  },
  nav: {
    logo: 'Peerex Peer',
    home: 'Home',
    directory: 'Directory',
    submissionCenter: 'Submission Center',
    submissionRules: 'Submission Rules',
    onlineSubmission: 'Online Submission',
    profile: 'Profile',
    profileInfo: 'Profile Info',
    accountSecurity: 'Account Security',
    messages: 'Messages',
    operationLogs: 'Operation Logs',
    manuscriptStatus: 'Manuscript Status',
    feedbackManagement: 'Feedback',
    helpCenter: 'Help Center',
    faq: 'FAQ',
    contact: 'Contact Us',
    feedback: 'Feedback',
    adminLogin: 'Admin Login',
    logout: 'Logout',
    login: 'Login',
    readOnly: 'Read-Only',
    readOnlyMode: 'Read-Only Mode',
    submitSystem: 'Submit System',
    userRole: 'User Role',
    register: 'Register',
    dashboard: 'Dashboard',
    roleSwitch: 'Role Switch',
    roles: {
      admin: 'Administrator Workspace',
      editor: 'Editor-in-Chief Workspace',
      associate_editor: 'Associate Editor Workspace',
      ea_ae: 'EA/AE Workspace',
      reviewer: 'Reviewer Workspace',
      author: 'Author Workspace'
    },
    tasks: 'Audit Tasks',
    history: 'Audit History',
    returnMain: 'Return to Main Site',
    roleManagement: 'Role Management',
    userList: 'User List',
    reviewerManagement: 'Reviewer Management',
    auditReviewerManagement: 'Reviewer Mgmt',
    auditRecommendedReviewers: 'Recommended',
    auditOpposedReviewers: 'Opposed',
    auditMyTasks: 'My Tasks',
    accountStatus: 'Account Status',
    systemSettings: 'System Settings',
    basicConfig: 'Basic Config',
    notificationSettings: 'Notifications',
    logManagement: 'Logs',
    moduleManagement: 'Modules',
    inviteCodeManagement: 'Invite Codes',
    manuscriptManagement: 'Manuscript Mgmt',
    newSubmission: 'New Submission',
    myManuscripts: 'My Manuscripts',
    manuscriptProgress: 'Progress',
    historySubmission: 'History',
    submissionGuide: 'Guide',
    onlineConsultation: 'Consultation',
    permissionDenied: 'Permission Denied',
    authorResources: 'Author Resources',
    guideForAuthors: 'Guide for Authors',
    templates: 'Templates',
    checkStatus: 'Check Status',
    letters: 'Letters',
    lettersAndInvitations: 'Letters & Invitations',
    logoutSubmit: 'Logout (Submit System)',
    myAssignments: 'My Assignments',
    auditTasks: 'Audit Tasks',
    reviewProcess: 'Review Process',
    publicationAnalytics: 'Publication & Analytics',
    publication: 'Publication',
    dataStatistics: 'Data Statistics',
    boardManagement: 'Board Management',
    adminTools: 'Admin Tools',
    editorManagement: 'Editor Management',
    journals: 'Journals',
    submit: 'Submit',
    resources: 'Resources',
    becomeReviewer: 'Become a Reviewer',
    reviewerGuidelines: 'Reviewer Guidelines',
    reviewerTraining: 'Reviewer Training',
    newsEvents: 'News & Events',
    latestArticles: 'Latest Articles',
    callForPapers: 'Call for Papers',
    upcomingEvents: 'Upcoming Events',
    reviewer: 'Reviewer',
    myReviews: 'My Reviews',
    myProfile: 'My Profile',
    help: 'Help',
    more: 'More',
    editorialBoard: 'Editorial Board',
    journalInfo: 'Journal Info',
    searchPlaceholder: 'Search articles, authors, DOI...',
    settings: 'Settings',
    auditNewSubmissions: 'New Submissions',
    auditAssignReviewers: 'Assign Reviewers',
    auditReviewMonitoring: 'Review Monitoring',
    auditDecisionMaking: 'Decision Making',
    auditRevisionHandling: 'Revision Handling',
    reviewers: 'Reviewers',
    decisionsLetters: 'Decisions & Letters',
    manuscripts: 'Manuscripts',
    profileSettings: 'Profile Settings',
    helpSupport: 'Help & Support'
  },
  home: {
    topBar: 'Welcome to the Peerex Peer Platform',
    hero: {
      title: 'Advancing Science, Together',
      subtitle: 'A modern platform for academic excellence and peer-reviewed research.',
      submit: 'Submit Your Manuscript'
    },
    sections: {
      latestArticles: 'Latest Articles',
      journalFamily: 'Our Journal Family',
      specialCollections: 'Special Collections'
    },
    journalFamily: {
      main: 'Main Journal',
      letters: 'Letters',
      reviews: 'Reviews',
      caseReports: 'Case Reports'
    },
    subscribe: {
      title: 'Stay Informed',
      text: 'Subscribe to our newsletter to receive the latest research and updates.'
    }
  },
  journalDetail: {
    header: {
      volume: 'Volume',
      issue: 'Issue',
      pages: 'Pages',
      publishedOnline: 'Published Online',
      correspondence: 'Correspondence',
      affiliations: 'Affiliations'
    },
    actions: {
      downloadPdf: 'Download PDF',
      cite: 'Cite'
    },
    sections: {
      abstract: 'Abstract',
      keywords: 'Keywords',
      mainText: 'Main Text'
    },
    abstract: {
      background: 'Background',
      methods: 'Methods',
      findings: 'Findings',
      interpretation: 'Interpretation',
      funding: 'Funding'
    },
    mainText: {
      introduction: 'Introduction',
      methods: 'Methods',
      results: 'Results',
      discussion: 'Discussion'
    }
  },
  reviewerDashboard: {
    stats: {
      pendingReviews: 'Pending Reviews',
      completedReviews: 'Completed Reviews',
      overdueReviews: 'Overdue Reviews'
    },
    status: {
      pending: 'Pending',
      completed: 'Completed',
      overdue: 'Overdue'
    },
    tasks: {
      title: 'My Review Tasks',
      empty: 'No review tasks found.',
      dueDate: 'Due Date',
      overdue: 'Overdue'
    },
    invitations: {
      title: 'Latest Invitations',
      viewAll: 'View All',
      empty: 'No new invitations.'
    },
    announcements: {
      title: 'System Announcements'
    }
  },
  preview: {
    title: 'Previewing {name}',
    download: 'Download',
    close: 'Close',
    loading: 'Loading preview...',
    fileType: 'File Type',
    size: 'Size',
    pdfError: 'Failed to load PDF. Please download to view.',
    imgError: 'Failed to load image.',
    txtError: 'Failed to load text content.',
    unsupported: 'This file type does not support online preview. Please download to view.'
  },
  allPending: {
    author: 'Author'
  },
  status: {
    // ManuscriptStatus - 25 states
    submitted: 'Submitted',
    pending_screen: 'Pending Screen',
    screen_expired: 'Screen Expired',
    initial_review_in_progress: 'Initial Review In Progress',
    initial_review_passed: 'Initial Review Passed',
    initial_review_rejected: 'Initial Review Rejected',
    reviewer_assignment_pending: 'Reviewer Assignment Pending',
    under_peer_review: 'Under Peer Review',
    review_completed: 'Review Completed',
    pending_final_decision: 'Pending Final Decision',
    final_decision_in_progress: 'Final Decision In Progress',
    final_decision_revision: 'Final Decision - Revision',
    final_decision_rejected: 'Final Decision - Rejected',
    final_decision_accepted: 'Final Decision - Accepted',
    author_revising: 'Author Revising',
    revision_submitted: 'Revision Submitted',
    pending_acceptance_confirmation: 'Pending Acceptance Confirmation',
    author_confirmed: 'Author Confirmed',
    in_production: 'In Production',
    production_completed: 'Production Completed',
    accepted_for_publish: 'Accepted for Publish',
    published: 'Published',
    rejected: 'Rejected',
    withdrawn: 'Withdrawn',
    transfer_suggested: 'Transfer Suggested',
    transferred: 'Transferred',
    // Legacy / alias
    under_review: 'Under Review',
    re_review: 'Re-review',
    pending_initial_review: 'Pending Initial Review'
  },
  workflowActions: {
    save: 'Save',
    submit: 'Submit',
    withdraw: 'Withdraw',
    screen: 'Screen',
    assign: 'Assign',
    review: 'Review',
    decide: 'Decide',
    revise: 'Revise',
    approve: 'Approve',
    publish: 'Publish'
  },
  decisionTypes: {
    accept: 'Accept',
    reject: 'Reject',
    revision: 'Revision',
    transfer: 'Transfer'
  },
  roles: {
    admin: 'Administrator',
    editor: 'Editor',
    associate_editor: 'Associate Editor',
    ea_ae: 'Editorial Assistant / Associate Editor',
    reviewer: 'Reviewer',
    author: 'Author',
    user: 'User'
  },
  footer: {
    about: {
      title: 'About',
      us: 'About Us',
      mission: 'Mission',
      team: 'Team',
      contact: 'Contact'
    },
    journals: {
      title: 'Journals'
    },
    authors: {
      title: 'Authors',
      instructions: 'Instructions for Authors',
      guidelines: 'Submission Guidelines',
      process: 'Peer Review Process',
      ethics: 'Publication Ethics'
    },
    resources: {
      title: 'Resources',
      faq: 'FAQ',
      help: 'Help Center',
      privacy: 'Privacy Policy',
      terms: 'Terms of Service'
    },
    rights: 'All rights reserved.'
  },
  submission: {
    brand: 'Submission Module',
    nav: {
      home: 'Home',
      about: 'About',
      help: 'Help',
      mainMenu: 'Main Menu',
      submitManuscript: 'Submit a Manuscript',
      letters: 'Letters',
      editorialBoard: 'Editorial Board',
      journalInfo: 'Journal Info',
      history: 'History',
      helpCenter: 'Help Center',
      submissionRules: 'Submission Rules',
      feedback: 'Feedback',
      logout: 'Logout'
    },
    sidebar: {
      instruction: 'Instruction for Authors',
      about: 'About the Journal',
      checklist: 'Pre-submission checklist',
      reviewers: 'Peer Reviewers'
    },
    welcome: {
      title: 'Welcome to Submission Module for',
      platform: 'Peerex Peer'
    },
    login: {
      title: 'Login to Submit System',
      username: 'Username',
      password: 'Password',
      placeholder: {
        username: 'Username',
        password: 'Password'
      },
      btn: {
        author: 'Author Login',
        reviewer: 'Reviewer Login',
        editor: 'Editor / Admin Login'
      },
      orcid: {
        label: 'ORCID® provides a persistent digital identifier that distinguishes you from every other researcher.',
        btn: 'Login with ORCID',
        help: 'What is ORCID?',
        info: 'You can use your ORCID iD to log in to our submission system. If you don\'t have one, you can register for one during the login process.'
      },
      link: {
        sendDetails: 'Send Login Details',
        register: 'Register Now',
        help: 'Login Help'
      },
      error: {
        required: 'Please enter both username and password.',
        failed: 'Login failed. Please check your credentials.'
      }
    },
    register: {
      title: 'Peerex Peer - Register Account',
      alreadyHaveAccount: 'Already have an account?',
      backToLogin: 'Login now',
      btn: {
        continue: 'Continue >>',
        complete: 'Complete Registration'
      },
      error: {
        required: 'Please fill in all required fields',
        passwordLength: 'Password length must be at least 6 characters'
      },
      fields: {
        firstName: 'Given/First Name',
        lastName: 'Family/Last Name',
        email: 'E-mail Address',
        username: 'Preferred User Name',
        password: 'Password',
        confirmPassword: 'Re-type Password',
        title: 'Title',
        middleName: 'Middle Name',
        degree: 'Degree',
        orcid: 'ORCID iD',
        position: 'Position',
        institution: 'Institution',
        department: 'Department',
        streetAddress: 'Street Address',
        city: 'City',
        stateProvince: 'State or Province',
        zipCode: 'Zip or Postal Code',
        country: 'Country or Region',
        classifications: 'Personal Classifications',
        keywords: 'Personal Keywords'
      },
      placeholder: {
        firstName: 'Enter your first name',
        lastName: 'Enter your last name',
        email: 'Enter your email address',
        username: 'Enter your username',
        password: 'Enter your password',
        confirmPassword: 'Re-enter your password',
        title: 'Enter your title',
        middleName: 'Enter your middle name',
        degree: 'Enter your degree',
        orcid: 'Enter your ORCID',
        position: 'Enter your position',
        institution: 'Enter your institution',
        department: 'Enter your department',
        streetAddress: 'Enter your street address',
        city: 'Enter your city',
        stateProvince: 'Enter your state or province',
        zipCode: 'Enter your zip code',
        country: 'Select country or region'
      },
      step1: {
        title: 'Choose a Registration Method',
        orcidLabel: 'Retrieve your details from the ORCID registry:',
        orcidBtn: 'Use My ORCID Record',
        manualLabel: 'Or type in your details and continue to register without using ORCID:',
        warning: {
          title: 'WARNING',
          msg1: 'If you think you already have an existing registration of any type (Author, Reviewer, or Editor) in this system, please DO NOT register again. This will cause delays or prevent the processing of any manuscript you submit.',
          msg2: 'If you are unsure if you are already registered, click the "Forgot Your Login Details?" button.'
        }
      },
      step2: {
        title: 'Login Details',
        info1: 'The username you choose must be unique within the system.',
        info2: 'If the one you choose is already in use, you will be asked for another.',
        passwordRules: 'Password Rules'
      },
      step3: {
        title: 'Personal Information',
        degreeHint: '(Ph.D., M.D., etc.)',
        emailInfo: 'If entering more than one e-mail address, use a semi-colon between each address.',
        orcidInfo1: 'You are encouraged to link to your ORCID ID and authenticate it.',
        orcidInfo2: 'You will only need to do this once in this journal.',
        orcidFetchBtn: 'Fetch/Register',
        whatIsOrcid: 'What is ORCID?'
      },
      step4: {
        title: 'Institution Related Information',
        institutionHint: 'Start typing to display potentially matching institutions.'
      },
      step5: {
        title: 'Areas of Interest or Expertise',
        info: 'Please indicate your areas of expertise by selecting from the pre-defined list or adding keywords.',
        noneSelected: '(None Selected)',
        noneDefined: '(None Defined)',
        selectBtn: 'Select Personal Classifications',
        editKeywordsBtn: 'Edit Personal Keywords',
        requiredNote: 'Select 1+ Classifications',
        finalInfo: 'After successful registration, additional details can be added via the "Update My Information" page.'
      }
    },
    about: {
      title: 'About the Submission System',
      description: 'This module is dedicated to manuscript submission, peer review, and editorial workflows.'
    },
    feedback: {
      title: 'Feedback',
      tabs: {
        submit: 'Submit Feedback',
        my: 'My Feedback',
        all: 'All Feedback (Editor)'
      },
      form: {
        type: 'Feedback Type',
        title: 'Title (Required, ≤50 chars)',
        description: 'Detailed Description (Required, ≥20 chars)',
        attachments: 'Attachments (Max 3, JPG/PNG/PDF, ≤5MB each)',
        contact: 'Contact Email',
        placeholder: {
          title: 'Brief summary',
          description: 'Describe your issue or suggestion...'
        },
        types: {
          suggestion: 'Feature Suggestion',
          bug: 'Bug Report',
          question: 'Usage Question',
          others: 'Others'
        }
      },
      alert: {
        maxFiles: 'Maximum 3 files allowed',
        fileSize: 'Some files exceed 5MB limit',
        success: 'Feedback submitted. We will reply within 2 business days. ID: {id}'
      }
    },
    help: {
      title: 'Help Center',
      search: 'Search for help...',
      searchBtn: 'Search',
      categories: {
        dashboard: 'Dashboard',
        manuscripts: 'Manuscripts',
        reviewers: 'Reviewers',
        decisions: 'Decisions & Letters',
        profile: 'Profile & Settings',
        manual: 'Operation Manual'
      },
      favorites: 'My Favorites',
      noFavorites: 'No favorites yet.',
      noArticles: 'No articles found in this category.',
      faq: 'Frequently Asked Questions',
      removeFav: 'Remove'
    }
  },
  auth: {
    adminLogin: {
      title: 'Administrative Portal',
      username: 'Admin Username',
      password: 'Security Password',
      rememberMe: 'Remember Me',
      submit: 'Access Dashboard',
      error: {
        accessDenied: 'Access Denied: This account does not have administrative privileges.',
        accountNotFound: 'Account not found. Please check your username.',
        invalidPassword: 'Invalid password. Please try again.',
        connectionError: 'A connection error occurred. Please verify your network.'
      }
    },
    register: {
      title: 'Create Account',
      subtitle: 'Join our academic community',
      desc: 'Submit your research and participate in the peer review process.',
      usernameLabel: 'Username',
      usernamePlaceholder: 'Enter your username',
      emailLabel: 'Email',
      emailPlaceholder: 'Enter your email',
      passwordLabel: 'Password',
      passwordPlaceholder: 'Enter your password',
      confirmPasswordLabel: 'Confirm Password',
      confirmPasswordPlaceholder: 'Confirm your password',
      invitationCodeLabel: 'Invitation Code (Optional)',
      invitationCodePlaceholder: 'Enter code for specialized roles',
      invitation: {
        valid: "Code valid. Assigned Role: {role}",
        invalid: "Invalid or expired invitation code.",
        verifying: "Verifying code...",
        error: "Failed to verify invitation code."
      },
      errors: {
        emailFormat: 'Invalid email format',
        passwordLength: 'Password must be at least 6 characters',
        passwordMatch: 'Passwords do not match.',
        frequencyLimit: 'Too many attempts. Please wait a while.',
        invalidInviteCode: 'Please provide a valid invitation code.',
        registrationFailed: 'Registration failed. Please check your details.',
        internalError: 'An internal server error occurred.'
      }
    }
  },
  dashboard: {
    roles: {
      admin: 'Administrator Workspace',
      editor: 'Editor-in-Chief Workspace',
      associate_editor: 'Associate Editor Workspace',
      ea_ae: 'EA/AE Workspace',
      default: 'Dashboard'
    },
    welcome: 'Welcome, {name}',
    stats: {
      totalJournals: 'Total Journals',
      pendingJournals: 'Pending Journals',
      totalUsers: 'Total Users',
      recentSubmissions: 'Recent Submissions',
      authorRecommendations: 'Author Recommendations',
      pendingApproval: 'Pending Approval',
      avoidanceRequests: 'Avoidance Requests',
      pendingReview: 'Pending Review'
    },
    recentJournals: {
      title: 'Recent Journals',
      author: 'Author',
      date: 'Date'
    },
    userRoles: {
      title: 'User Role Distribution',
      admin: 'Administrators',
      editor: 'Editors',
      associate_editor: 'Associate Editors',
      ea_ae: 'EA/AE',
      reviewer: 'Reviewers',
      author: 'Authors'
    }
  },
  review: {
    title: 'Review Form',
    dimensions: {
      addressingPreviousConcerns: 'Addressing of Previous Concerns',
      qualityOfRevisions: 'Quality of Revisions',
      newIssuesIdentified: 'New Issues Identified',
      originality: 'Originality',
      methodology: 'Methodology',
      ethicalCompliance: 'Ethical Compliance',
      readability: 'Readability',
      importance: 'Importance'
    },
    levels: {
      excellent: 'Excellent',
      good: 'Good',
      fair: 'Fair',
      poor: 'Poor'
    },
    comments: {
      toAuthor: 'Review Comments (To Author)',
      toEditor: 'Confidential Comments (To Editor)',
      placeholder: 'Enter your review comments here...'
    },
    decision: {
      label: 'Recommendation',
      accept: 'Accept',
      minorRevision: 'Minor Revision',
      majorRevision: 'Major Revision',
      reject: 'Reject'
    },
    actions: {
      submit: 'Submit Review',
      cancel: 'Cancel',
      saveDraft: 'Save Draft'
    },
    validation: {
      required: 'This field is required',
      selectAllDimensions: 'Please select a rating level for all required review criteria',
      provideComments: 'Please provide review comments for the author',
      selectDecision: 'Please select a final recommendation for the manuscript'
    },
    confirmation: {
      title: 'Confirm Submission',
      message: 'Are you sure you want to submit this review? This action cannot be undone, and the review will be immediately available to the editorial team.'
    }
  },
  history: {
    title: {
      allHistory: 'All History',
      manuscriptHistory: 'Manuscript History',
      operationHistory: 'Operation History',
      submissionHistory: 'Submission History',
      reviewHistory: 'Review History'
    },
    noRecords: 'No records found',
    filters: {
      module: 'Module',
      status: 'Status',
      timeRange: 'Time Range',
      keyword: 'Keyword Search',
      searchPlaceholder: 'Search title, author or keywords...',
      allModules: 'All Modules',
      allStatus: 'All Status',
      allTime: 'All Time',
      today: 'Today',
      week: 'This Week',
      month: 'This Month',
      year: 'This Year'
    },
    table: {
      title: 'Title',
      author: 'Author',
      module: 'Module',
      status: 'Status',
      submitDate: 'Submission Date',
      reviewDate: 'Review Date',
      date: 'Date',
      actions: 'Actions',
      viewDetail: 'View Details',
      operator: 'Operator',
      action: 'Action',
      notes: 'Notes'
    },
    status: {
      accepted: 'Accepted',
      rejected: 'Rejected',
      pending: 'Pending',
      underReview: 'Under Review',
      revisionRequested: 'Revision Requested',
      published: 'Published',
      submitted: 'Submitted',
      initial: 'Initial Review',
      peer: 'Peer Review',
      final: 'Final Review',
      statusChangedTo: 'Status changed to',
      submissionSuccess: 'Manuscript submitted successfully.'
    },
    action: {
      statusUpdate: 'Status Update'
    },
    reviewComment: 'Review Comments',
    noComment: 'No comments',
    expandAll: 'Expand All',
    collapse: 'Collapse',
    export: 'Export Data',
    reset: 'Reset Filters',
    pagination: {
      total: 'Total {total} records',
      page: 'Page {current} / {total}',
      prev: 'Previous',
      next: 'Next'
    }
  },
  notification: {
    title: 'System Settings - Notification Settings',
    subtitle: 'Manage platform notification templates and reminder rules',
    reminderRules: {
      title: 'Reminder Rules',
      enableEmail: 'Enable Email Notification',
      enableEmailDesc: 'Send notifications via email',
      enableSMS: 'Enable SMS Notification',
      enableSMSDesc: 'Send notifications via SMS',
      submissionReminder: 'Post-submission Notification (Hours)',
      reviewReminder: 'Post-review Notification (Hours)',
      statusUpdateReminder: 'Status Update Notification (Hours)',
      reviewInterval: 'Review Cycle Reminder (Days)',
      placeholder: 'Enter notification time'
    },
    emailTemplates: {
      title: 'Email Templates',
      submissionSuccess: 'Submission Success',
      reviewResult: 'Review Result',
      statusUpdate: 'Status Update',
      reviewerInvitation: 'Reviewer Invitation',
      recommendationResult: 'Recommendation Result',
      subject: 'Email Subject',
      content: 'Email Content',
      placeholderSubject: 'Enter email subject',
      placeholderContent: 'Enter email content',
      tips: 'Available variables:'
    },
    smsTemplates: {
      title: 'SMS Templates',
      submissionSuccess: 'Submission Success',
      reviewResult: 'Review Result',
      statusUpdate: 'Status Update',
      content: 'SMS Content',
      placeholder: 'Enter SMS content'
    },
    announcement: {
      title: 'Announcement Settings',
      desc: 'Manage platform announcements displayed on the homepage',
      addTitle: 'New Announcement',
      editTitle: 'Edit Announcement',
      listTitle: 'Announcement List',
      form: {
        title: 'Title',
        content: 'Content',
        titlePlaceholder: 'Enter announcement title',
        contentPlaceholder: 'Enter announcement content'
      },
      actions: {
        add: 'Add Announcement',
        saveEdit: 'Save Changes',
        cancel: 'Cancel',
        edit: 'Edit',
        delete: 'Delete',
        confirmDelete: 'Are you sure you want to delete this announcement?'
      },
      empty: 'No announcements yet. Please add the first one.'
    },
    actions: {
      reset: 'Reset',
      save: 'Save Configuration',
      saveSuccess: 'Notification configuration saved!',
      resetSuccess: 'Configuration reset to default!',
      addSuccess: 'Announcement added successfully!',
      editSuccess: 'Announcement edited successfully!',
      deleteSuccess: 'Announcement deleted successfully!',
      incomplete: 'Please fill in complete announcement information'
    },
    basicConfig: {
      title: 'System Settings - Basic Configuration',
      subtitle: 'Manage platform basic information and rules',
      platformInfo: {
        title: 'Platform Information',
        name: 'Platform Name',
        logo: 'Platform Logo',
        placeholderName: 'Enter platform name',
        placeholderLogo: 'Click to upload Logo'
      },
      contact: {
        title: 'Contact Information',
        email: 'Contact Email',
        phone: 'Contact Phone',
        placeholderEmail: 'Enter contact email',
        placeholderPhone: 'Enter contact phone'
      },
      rules: {
        title: 'Submission Rules',
        label: 'Submission Rules',
        placeholder: 'Enter submission rules'
      },
      copyright: {
        title: 'Copyright Information',
        label: 'Copyright Information',
        placeholder: 'Enter copyright information'
      },
      actions: {
        reset: 'Reset',
        save: 'Save Configuration',
        saveSuccess: 'Basic configuration saved!',
        resetSuccess: 'Configuration reset to default!'
      }
    }
  },
  reviewer: {
    dashboard: 'Reviewer Dashboard',
    stats: {
      totalJournals: 'Total Submissions',
      pendingJournals: 'Pending Reviews',
      stage1Journals: 'Initial Review',
      stage2Journals: 'Peer Review'
    },
    pendingList: {
      title: 'Pending Reviews',
      empty: 'No pending reviews',
      author: 'Author',
      date: 'Date',
      module: 'Module'
    },
    status: {
      pending: 'Pending',
      reviewing: 'Under Review',
      stage1: 'Initial Review',
      stage2: 'Peer Review',
      stage3: 'Final Decision',
      accepted: 'Accepted',
      rejected: 'Rejected'
    },
    permissionDenied: 'You do not have permission to access the Reviewer Dashboard'
  },
  author: {
    dashboard: 'Author Dashboard',
    stats: {
      totalJournals: 'Total Submissions',
      pendingJournals: 'Pending',
      passedJournals: 'Accepted',
      rejectedJournals: 'Rejected',
      transferJournals: 'Transfer Suggested'
    },
    quickActions: {
      newSubmission: '+ New Submission'
    },
    mySubmissions: {
      title: 'My Submissions',
      empty: 'No submissions yet',
      date: 'Date',
      module: 'Module',
      transferAction: 'Review Transfer'
    },
    transferDetails: {
      title: 'Transfer Recommendation',
      suggestedJournal: 'Recommended Journal',
      reason: 'Editor\'s Note',
      acceptBtn: 'Accept Transfer',
      declineBtn: 'Decline Transfer',
      acceptConfirm: 'Are you sure you want to transfer this manuscript to the recommended journal?',
      declineConfirm: 'If you decline, your manuscript will be considered withdrawn from the current journal. Do you want to proceed?',
      successAccept: 'Manuscript successfully transferred.',
      successDecline: 'Transfer declined. Manuscript withdrawn.'
    },
    permissionDenied: 'You do not have permission to access the Author Dashboard'
  },
  logs: {
    title: 'System Settings - Logs Management',
    subtitle: 'Manage platform operation logs, login logs, and error logs.',
    types: {
      all: 'All Logs',
      operation: 'Operation Logs',
      login: 'Login Logs',
      error: 'Error Logs'
    },
    filters: {
      searchPlaceholder: 'Search logs...',
      startDate: 'Start Date',
      endDate: 'End Date',
      reset: 'Reset',
      to: 'to'
    },
    actions: {
      export: 'Export',
      clear: 'Clear Logs',
      confirmClearTitle: 'Confirm Clear Logs',
      confirmClearMessage: 'Are you sure you want to clear all logs? This action cannot be undone!',
      cancel: 'Cancel',
      confirm: 'Clear All'
    },
    table: {
      id: 'ID',
      type: 'Type',
      user: 'User',
      action: 'Action',
      target: 'Target',
      ip: 'IP Address',
      time: 'Time',
      status: 'Status',
      empty: 'No matching logs found'
    }
  },
  clinicalTerminology: {
    irbApproval: 'Institutional Review Board (IRB) Approval',
    informedConsent: 'Informed Consent Statement',
    dataAvailability: 'Data Availability Statement',
    conflictOfInterest: 'Declaration of Competing Interest',
    fundingStatement: 'Funding Statement',
    authorshipContribution: 'Author Contributions (ICMJE)',
    orcidRequirement: 'ORCID iD Required for All Authors',
    patientConsent: 'Patient Consent Form Required',
    clinicalTrialRegistration: 'Clinical Trial Registration Number'
  },
  guide: {
    downloadPdf: 'Download Full Guide PDF',
    preparation: {
      title: 'Preparation',
      desc: 'Before submitting your manuscript, please ensure you have read the following guidelines carefully. Adherence to these guidelines will ensure a smooth review process.',
      ethicsTitle: 'Ethics & Disclosure',
      ethicsDesc: 'All authors must disclose any financial and personal relationships with other people or organizations that could inappropriately influence (bias) their work.'
    },
    formatting: {
      title: 'Formatting',
      textTitle: 'Text Formatting',
      textDesc: 'Manuscripts should be submitted in Word format. Use a standard font (e.g., Times New Roman, Arial) at 12 pt size. Double-space the entire manuscript.',
      figuresTitle: 'Figures & Tables',
      figuresDesc: 'Figures should be high-resolution (min 300 dpi). Tables should be editable text, not images.'
    },
    process: {
      title: 'Review Process',
      desc: 'Our journal follows a double-blind peer review process. All manuscripts are initially screened by the editor. Manuscripts that meet the journal\'s standards are sent to at least two independent reviewers.'
    },
    policies: {
      title: 'Policies',
      openAccessTitle: 'Open Access',
      openAccessDesc: 'We offer authors the option to make their article open access. A publication fee applies.',
      copyrightTitle: 'Copyright',
      copyrightDesc: 'Authors retain copyright of their work under a Creative Commons Attribution License.'
    },
    faq: {
      title: 'FAQ',
      searchPlaceholder: 'Search FAQs...'
    },
    toast: 'PDF download started...',
    articleTypes: {
      original: {
        title: 'Original Research',
        structure: 'Manuscripts should include: Introduction, Methods, Results, Discussion, and Conclusion.',
        abstract: 'A structured abstract is required with four sections: Background, Methods, Findings, and Interpretation.',
        figures: 'Maximum 5 figures and/or tables.',
        ethics: 'Must include IRB approval, patient consent, and data sharing statements.'
      },
      review: {
        title: 'Review Article',
        structure: 'Comprehensive reviews with clear headings and logical flow.',
        abstract: 'Unstructured abstract summarizing the main points.',
        figures: 'Maximum 8 figures and/or tables.',
        ethics: 'Conflict of interest statement required.'
      },
      caseReport: {
        title: 'Case Report',
        structure: 'Should include: Introduction, Case Presentation, Discussion, and Conclusion.',
        abstract: 'Unstructured abstract summarizing the case.',
        figures: 'Maximum 3 figures and/or tables.',
        ethics: 'Patient consent for publication must be obtained and stated.'
      }
    }
  },
  templates: {
    filters: {
      subject: 'Subject:',
      type: 'Type:',
      allSubjects: 'All Subjects',
      medicine: 'Medicine',
      biology: 'Biology',
      publicHealth: 'Public Health',
      original: 'Original Research',
      review: 'Review',
      caseReport: 'Case Report'
    },
    preview: 'Preview',
    download: 'Download',
    toast: 'Template download started.',
    list: {
      originalResearch: 'Original Research Template',
      systematicReview: 'Systematic Review Template',
      caseReport: 'Case Report Template',
      biologyResearch: 'Biology Research Template',
      publicHealth: 'Public Health Survey',
      clinicalTrial: 'Clinical Trial Protocol'
    }
  },
  news: {
    events: {
      title: 'Upcoming Events',
      register: 'Register',
      watchReplay: 'Watch Replay',
      addToCalendar: 'Add to Calendar',
      toastRegister: 'Registration for "{title}" opened.',
      toastReplay: 'Opening replay for "{title}"...'
    },
    calls: {
      title: 'Call for Papers',
      intro: 'Submit your manuscript to our upcoming special issues.',
      deadline: 'Deadline:',
      guestEditor: 'Guest Editor:',
      submitNow: 'Submit Now',
      pastIssues: 'Past Special Issues',
      ended: 'Ended {date}'
    }
  }
}
