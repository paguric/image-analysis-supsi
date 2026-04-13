import * as React from 'react'
import Button from '@mui/material/Button'
import Dialog from '@mui/material/Dialog'
import DialogActions from '@mui/material/DialogActions'
import DialogContent from '@mui/material/DialogContent'
import DialogContentText from '@mui/material/DialogContentText'
import DialogTitle from '@mui/material/DialogTitle'

function ConfirmationAlert({ open, onContinue, onAbort, firstVideoFrameCount, secondVideoFrameCount, totalFrameCount}) {
  return (
    <Dialog open={open} aria-labelledby="alert-dialog-title">
      <DialogTitle id="alert-dialog-title">
        Frame count mismatch
      </DialogTitle>
      <DialogContent>
        <DialogContentText>
          The two videos have a different number of frames (video before: {firstVideoFrameCount} vs video after: {secondVideoFrameCount}).
          The analysis may produce inaccurate results. If you continue, the longer video will be cut to {totalFrameCount}.
          Do you want to continue anyway?
        </DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={onAbort} color="error" variant="outlined">
          Abort
        </Button>
        <Button onClick={onContinue} autoFocus variant="contained">
          Continue anyway
        </Button>
      </DialogActions>
    </Dialog>
  )
}

export default ConfirmationAlert