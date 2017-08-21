#!/usr/env python
import numpy as np
class Read():
	def __init__(self):
		self.name=None
		self.alignments=[]
		self.forward=0
		self.reverse=0
		self.inversion=False
		self.insertion=None
		self.strandPix=None
		self.sameStrand=None
		self.startClip=None
		self.endClip=None
		self.mapq=None
		self.score=None
	def label(self,name): self.name=name
	def strandIncrement(self,strand=None):
		if strand=='+': self.forward+=1
		else: self.reverse+=1
	def loadAlignments(self,aln): self.alignments.append(aln)
	def pixelPrep(self,MAX=None,start=None,end=None,svtype=None,minInv=None):
		self.countStrands()
		self.prepAlignments(MAX,start,end,svtype,minInv)
		self.scoreAlignments()
	def countStrands(self):
		self.strandPix='+'
		if self.reverse > self.forward: self.strandPix='-'
		if self.forward>0 and self.reverse>0: self.sameStrand=False
	def prepAlignments(self,MAX=None,start=None,end=None,svtype=None,minInv=None):
		q=[]		
		for Aln in self.alignments:
			q.append(Aln.mapq)
			if svtype != 'INV': continue
			if self.sameStrand==True: continue
			invpos=len([x for x in Aln.pos if start<=x<=end])
			outpos = len(Aln.pos)-invpos
			invOvr = float(invpos)/(invpos+outpos)
			if invOvr>=minInv: 
				self.inversion=1.-invOvr
				if self.strandPix==Aln.strand: 
					if self.strandPix=='+':self.strandPix='-'
					else: self.strandPix='+' 
		mapq=np.median(q)
		if mapq>MAX:mapq=MAX
		self.mapq=abs(MAX-mapq)
	def scoreAlignments(self): 
		score=sum([x for x in [self.startClip,self.endClip] if x!= None])
		if self.startClip!=None or self.endClip!=None: self.score=score
