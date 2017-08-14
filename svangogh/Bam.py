#!/usr/env python
import pysam,sys
from Alignment import Alignment
from Cigar import Cigar
from Read import Read
import numpy as np
from operator import itemgetter
def unionize(reads,qname,qAln):
	if reads.get(qname)!= None:
		read = reads[qname]
		read.loadAlignments(qAln)
		reads[qname]=read
	else:
		read=Read()
		read.label(qname)
		read.loadAlignments(qAln)
		reads[qname]=read
	return reads
class Bam():
	def __init__(self,SV=None,Args=None):
		self.ifh=Args.ifh
		self.bam = pysam.AlignmentFile(self.ifh,'rb')
		self.reads=None
		self.clips=None
		self.medStart=None
		self.medEnd=None
		self.verbose=Args.verbose
		READS={}
		CLIPS=[]
		if self.verbose==True: print "processing left breakpoint"
		for al in self.bam.fetch(str(SV.chrom),SV.leftCI[0]-Args.windowFlank,SV.leftCI[1]+Args.windowFlank):
			if al.cigarstring==None or len(al.get_reference_positions())==0: continue
			qAln, qCig = Alignment(al), Cigar(al.cigarstring)
			if SV.svtype=='INS': qAln.queryPos(qCig)
			qAln.setClips(qCig,al.reference_start,al.reference_end,SV.leftCI,SV.rightCI,)
			if SV.svtype=='DEL' or SV.svtype=='DUP':qAln.cigarSV(qCig.cig,al.reference_start,SV.start,SV.end,SV.svtype,SV.leftCI,SV.rightCI)
			CLIPS.append((qAln.startClip,qAln.endClip))
			READS=unionize(READS,al.query_name,qAln)
		if self.verbose==True: print "left breakpoint complete"
		if self.verbose==True: print "processing right breakpoint"
		for al in self.bam.fetch(str(SV.chrom),SV.rightCI[0]-Args.windowFlank,SV.rightCI[1]+Args.windowFlank):
			if al.cigarstring==None or len(al.get_reference_positions())==0: continue
			qAln, qCig = Alignment(al), Cigar(al.cigarstring)
			qAln.setClips(qCig,al.reference_start,al.reference_end,SV.leftCI,SV.rightCI)
			if SV.svtype=='DEL' or SV.svtype=='DUP':qAln.cigarSV(qCig.cig,al.reference_start,SV.start,SV.end,SV.svtype,SV.leftCI,SV.rightCI)
			CLIPS.append((qAln.startClip,qAln.endClip))
			READS=unionize(READS,al.query_name,qAln)
		if self.verbose==True: print "right breakpoint complete"
		self.clips=CLIPS
		self.reads=READS
		if SV.svtype=='INS': self.insertion()
		self.pixelPrep(SV)
	def insertion(self):
		if self.verbose==True: print "processing insertions"
		for name in self.reads:
			qPos,qGaps=[],[]
			if len(self.reads[name].alignments) < 1: continue
			for Aln in self.reads[name].alignments: qPos.append((Aln.qStart,Aln.qEnd,Aln.strand))
			alns = sorted(list(set(qPos)),key=itemgetter(0,1))
			for i in range(len(alns)-1):
				qGap = alns[i+1][0]-alns[i][1]
				if alns[i][2]==alns[i+1][2]:
					if qGap >= 20: qGaps.append(qGap)
			if len(qGaps)>0: self.reads[name].insertion=max(qGaps)
		if self.verbose==True: print "insertion processing complete"
	def pixelPrep(self,SV):
		if self.verbose==True: print "painting ..."
		self.medianClip(SV)
		self.assignClips()
		if self.medStart==self.medEnd: sys.stderr.write('ERROR: median start clip:{} is equal to the median end clip:{}\n'.format(self.medStart,self.medEnd))
	def medianClip(self,SV):
		start = [x[0] for x in self.clips if x[0] != None]
		end= [x[1] for x in self.clips if x[1] != None]
		if len(start)>0: self.medStart=int(np.median(start))
		else: self.medStart=SV.start
		if len(end)>0: self.medEnd=int(np.median(end))
		else: self.medEnd=SV.end
	def assignClips(self):
		for name in self.reads:
			Read=self.reads[name]
			start,end=[],[]
			for Aln in Read.alignments:
				if Aln.startClip!=None: start.append(abs(Aln.startClip-self.medStart))
				if Aln.endClip!=None: end.append(abs(Aln.endClip-self.medEnd))
			if len(start)>0: Read.startClip=sorted(start).pop(0)	
			if len(end)>0: Read.endClip=sorted(end).pop(0)
